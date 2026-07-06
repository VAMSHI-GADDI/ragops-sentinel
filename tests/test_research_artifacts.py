from pathlib import Path
import json
import subprocess
import sys


def test_generate_research_artifacts(tmp_path: Path):
    results = tmp_path / 'results'
    out = tmp_path / 'artifacts'
    results.mkdir()
    (results / 'm5_repair_benchmark.json').write_text(json.dumps({
        'aggregate': {
            'repair_success_rate': 1.0,
            'before_mean_stale_evidence_rate': 0.2,
            'after_mean_stale_evidence_rate': 0.0,
            'before_total_stale_chunks': 2,
            'after_total_stale_chunks': 0,
            'stale_chunk_reduction': 2,
            'before_mean_faithfulness': 0.7,
            'after_mean_faithfulness': 0.8,
            'before_mean_unsupported_claim_rate': 0.3,
            'after_mean_unsupported_claim_rate': 0.2,
        }
    }))
    completed = subprocess.run(
        [sys.executable, 'scripts/generate_research_artifacts.py', '--results-dir', str(results), '--output-dir', str(out)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert 'M8_PUBLICATION_PATENT_PACKAGE' in completed.stdout
    expected = {
        'artifact_summary.json',
        'technical_report.md',
        'ieee_paper_draft.md',
        'patent_screening_memo.md',
        'reproducibility_checklist.md',
    }
    assert expected.issubset({p.name for p in out.iterdir()})
    assert 'patentability is not claimed' in (out / 'patent_screening_memo.md').read_text(encoding='utf-8').lower()
