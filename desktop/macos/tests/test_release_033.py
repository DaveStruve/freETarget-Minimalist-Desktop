"""Static release guards for the 0.3.3 configurable Dashboard feature.
Browser behavior is separately covered by the optional Chromium acceptance suite.
"""
import json
import pathlib
import re
import unittest
from storage import validate_storage

ROOT=pathlib.Path(__file__).resolve().parents[1]
HTML=(ROOT/'app/assets/index.html').read_text(encoding='utf-8')

class DashboardReleaseTests(unittest.TestCase):
    def test_widget_catalog_has_six_panels_and_approved_sizes(self):
        expected={
            'scoring':"sizes:['small','large']",
            'recent':"sizes:['small','large']",
            'distribution':"sizes:['small','large']",
            'previous':"sizes:['small','large']",
            'scorecard':"sizes:['small','large']",
            'sessionDetails':"sizes:['small','large']",
        }
        for name,sizes in expected.items():
            self.assertRegex(HTML,rf"id:'{name}'.{{0,65}}{re.escape(sizes)}")

    def test_widget_layout_is_persisted_and_validated(self):
        self.assertIn("const DASHBOARD_LAYOUT_KEY='ft-dashboard-widgets-v1'",HTML)
        self.assertIn('function loadDashboardLayout()',HTML)
        self.assertIn('function saveDashboardLayout()',HTML)
        data={'ft-dashboard-widgets-v1':json.dumps([{'id':'scoring','size':'large','visible':True}])}
        self.assertEqual(validate_storage(data),data)

    def test_previous_target_keeps_square_aspect(self):
        self.assertIn('.dashboardWidgets .previousCard .previousTarget{width:100%!important',HTML)
        self.assertIn('aspect-ratio:1/1',HTML)

    def test_new_widgets_use_real_scoring_and_session_state(self):
        for text in ('function renderScorecard()', 'sightingShots.length', 'scorecardFocusSeries', 'function renderSessionDetails()', 'sessionElapsed()', 'runtime.phaseStart', 'function updateDashboardWidgetClock()'):
            self.assertIn(text,HTML)

    def test_layout_editor_has_keyboard_fallback_and_reset(self):
        for text in ('function moveWidgetStep(', 'function moveWidget(', 'function setWidgetVisible(', 'function setWidgetSize(', 'Reset Layout', 'Add / Remove Widgets'):
            self.assertIn(text,HTML)

if __name__=='__main__':unittest.main()
