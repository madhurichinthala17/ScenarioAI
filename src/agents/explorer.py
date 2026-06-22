import json
from typing import Optional

from src.agents.base import BaseAgent
from src.core.logger import get_logger
from src.models.state import ElementInfo, ExplorationReport

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a QA engineer mapping user requirement actions to Playwright locators.
Given a list of real UI elements and a requirement, return a JSON object mapping
each action described in the requirement to the best matching locator string.

Example output:
{
  "enter email": "input[name='email']",
  "enter password": "input[name='password']",
  "click login": "button[type='submit']"
}

Return JSON only. No explanations."""


class ExplorerAgent(BaseAgent):
    def run(self, app_url: str, requirement: str) -> Optional[ExplorationReport]:
        """
        Navigate to app_url with a real browser, collect interactive element locators,
        then use the LLM to map requirement actions to specific locators.

        Returns None if playwright is not installed or the page can't be reached —
        the caller treats None as "skip exploration, use LLM-guessed locators".
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            log.warning("Explorer: playwright not installed — skipping. Run: playwright install chromium")
            return None

        log.info("Explorer: navigating to %s", app_url)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                try:
                    # networkidle = wait until no network requests for 500ms
                    # more reliable than just waiting for DOMContentLoaded
                    page.goto(app_url, wait_until="networkidle", timeout=15000)
                    page_title = page.title()
                    elements = self._collect_elements(page)
                    locator_map = self._map_to_requirement(elements, requirement)
                    return {
                        "page_url": app_url,
                        "page_title": page_title,
                        "elements": elements,
                        "locator_map": locator_map,
                    }
                finally:
                    browser.close()
        except Exception as e:
            log.warning("Explorer: could not navigate to %s — %s. Skipping.", app_url, e)
            return None

    def _collect_elements(self, page) -> list[ElementInfo]:
        elements: list[ElementInfo] = []

        # Broad selector: grab all interactive elements at once
        handles = page.query_selector_all(
            "input, button, a[href], select, textarea, [role='button'], [role='link']"
        )

        for handle in handles[:60]:  # cap at 60 to avoid overwhelming the LLM
            try:
                tag = handle.evaluate("el => el.tagName.toLowerCase()")
                input_type = handle.get_attribute("type") or tag
                locator = self._best_locator(handle, tag)
                if not locator:
                    continue

                # Build a human-readable label in priority order
                label = (
                    handle.get_attribute("aria-label")
                    or handle.get_attribute("placeholder")
                    or handle.get_attribute("name")
                    or (handle.inner_text() or "")[:50]
                    or handle.get_attribute("id")
                    or ""
                ).strip()

                elements.append({"role": input_type, "label": label, "locator": locator})
            except Exception:
                # A stale or detached element — skip silently
                continue

        log.info("Explorer: found %d interactive elements", len(elements))
        return elements

    def _best_locator(self, handle, tag: str) -> str:
        """
        Return the most stable Playwright locator for an element.
        Priority order follows Playwright's own best-practice recommendations:
        data-testid > id > name > aria-label > text content > type attribute
        """
        try:
            # 1. data-testid — explicitly designed for testing, never changes with style
            testid = handle.get_attribute("data-testid")
            if testid:
                return f"[data-testid='{testid}']"

            # 2. id — very stable, unique per page
            el_id = handle.get_attribute("id")
            if el_id:
                return f"#{el_id}"

            # 3. name — stable for form inputs (tied to form submission logic)
            name = handle.get_attribute("name")
            if name and tag in ("input", "select", "textarea"):
                return f"{tag}[name='{name}']"

            # 4. aria-label — accessibility attribute, rarely changes
            aria = handle.get_attribute("aria-label")
            if aria:
                return f"[aria-label='{aria}']"

            # 5. visible text for buttons and links
            text = (handle.inner_text() or "").strip()[:30]
            if text and tag in ("button", "a"):
                return f"{tag}:has-text('{text}')"

            # 6. type attribute as last resort for inputs
            input_type = handle.get_attribute("type")
            if input_type and tag == "input":
                return f"input[type='{input_type}']"

        except Exception:
            pass
        return ""

    def _map_to_requirement(self, elements: list[ElementInfo], requirement: str) -> dict:
        """Use LLM to map natural language actions to the collected locators."""
        if not elements:
            return {}

        user_prompt = f"""Requirement:
{requirement}

Real UI elements found on the page:
{json.dumps(elements, indent=2)}

Map each user action in the requirement to the best locator from the list above.
Return JSON only."""

        try:
            response = self.llm.invoke(SYSTEM_PROMPT, user_prompt)
            return json.loads(self._strip(response))
        except Exception as e:
            log.warning("Explorer: LLM mapping failed (%s) — using raw labels as fallback", e)
            return {el["label"]: el["locator"] for el in elements if el["locator"]}
