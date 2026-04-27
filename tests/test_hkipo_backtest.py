import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hkipo_backtest import IpoSample, apply_futu_debut_returns, summarize_score_calibration


def make_sample(code: str, odds_score: int, debut_return_pct: float) -> IpoSample:
    return IpoSample(
        name=f"Sample {code}",
        code=code,
        listing_date="2026/01/01",
        market_cap_text="N/A",
        market_cap_mid_hkd_b=None,
        industry="other",
        offer_price=None,
        listing_price=None,
        oversub_rate=None,
        applied_lots_for_one_lot=None,
        one_lot_success_rate=None,
        last_price=None,
        debut_return_pct=debut_return_pct,
        accumulated_return_pct=None,
        heat_bucket="unknown",
        valuation_bucket="unknown",
        grey_market_return_pct=None,
        greenshoe=None,
        cornerstone=None,
        heat_score=None,
        industry_score=None,
        valuation_score=None,
        structure_score=None,
        grey_score=None,
        odds_score=odds_score,
    )


class ScoreCalibrationTest(unittest.TestCase):
    def test_summarizes_score_buckets_and_mismatches(self) -> None:
        samples = [
            make_sample("00001.HK", 95, 120.0),
            make_sample("00002.HK", 86, -8.0),
            make_sample("00003.HK", 70, 12.0),
            make_sample("00004.HK", 55, -15.0),
            make_sample("00005.HK", 45, 80.0),
        ]

        calibration = summarize_score_calibration(samples)

        self.assertEqual(
            [row["bucket"] for row in calibration["by_score_bucket"]],
            ["90-100", "80-89", "65-79", "50-64", "<50"],
        )
        self.assertEqual(calibration["by_score_bucket"][0]["count"], 1)
        self.assertEqual(calibration["by_score_bucket"][0]["win_rate"], 1.0)
        self.assertEqual(calibration["by_score_bucket"][1]["break_rate"], 1.0)
        self.assertGreater(calibration["score_return_rank_correlation"], 0)
        mismatch_codes = {row["code"] for row in calibration["mismatch_samples"]}
        self.assertIn("00002.HK", mismatch_codes)
        self.assertIn("00005.HK", mismatch_codes)


class FutuDebutReturnTest(unittest.TestCase):
    def test_applies_futu_first_day_close_to_debut_return(self) -> None:
        sample = make_sample("02635.HK", 62, 10.0)
        sample.listing_date = "2025/12/23"
        sample.offer_price = 80.0

        updated = apply_futu_debut_returns([sample], fetch_close=lambda code, date: 100.0)

        self.assertEqual(updated, 1)
        self.assertEqual(sample.debut_return_source, "futu_kline")
        self.assertEqual(sample.futu_debut_close, 100.0)
        self.assertEqual(sample.listed_table_debut_return_pct, 10.0)
        self.assertAlmostEqual(sample.debut_return_pct, 25.0)


if __name__ == "__main__":
    unittest.main()
