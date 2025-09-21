# app/services/reports/esg/generator.py
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any

from .sections import render_environment, render_social, render_governance, TPL_DIR
from .types import ESGReportContext, ESGSectionContext

_base_env = Environment(
    loader=FileSystemLoader(str(TPL_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def _ensure_env_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    metrics = dict(metrics or {})
    metrics.setdefault("overview", {})
    metrics.setdefault("trends", [])
    metrics.setdefault("actions", [])
    return metrics

def _ensure_soc_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    metrics = dict(metrics or {})
    metrics.setdefault("overview", {})
    metrics.setdefault("diversity", [])
    metrics.setdefault("safety", [])
    return metrics

def _ensure_gov_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    metrics = dict(metrics or {})
    metrics.setdefault("overview", {})
    metrics.setdefault("board", [])
    metrics.setdefault("policies", [])
    return metrics

def build_report_html(
    *,
    company_info: Dict[str, Any],
    period_label: str,
    summary_metrics: Dict[str, Any],
    env_metrics: Dict[str, Any],
    soc_metrics: Dict[str, Any],
    gov_metrics: Dict[str, Any],
) -> str:
    # 템플릿이 기대하는 키를 보장
    env_metrics = _ensure_env_metrics(env_metrics)
    soc_metrics = _ensure_soc_metrics(soc_metrics)
    gov_metrics = _ensure_gov_metrics(gov_metrics)

    # 각 섹션(2페이지 구성은 템플릿의 page-break로 처리)
    env_html = render_environment(ESGSectionContext(title="Environmental", metrics=env_metrics))
    soc_html = render_social(ESGSectionContext(title="Social", metrics=soc_metrics))
    gov_html = render_governance(ESGSectionContext(title="Governance", metrics=gov_metrics))

    base = _base_env.get_template("base.html")
    ctx = ESGReportContext(
        company=company_info,
        period_label=period_label,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        summary=summary_metrics or {},
        env=ESGSectionContext(title="Environmental", metrics=env_metrics),
        soc=ESGSectionContext(title="Social", metrics=soc_metrics),
        gov=ESGSectionContext(title="Governance", metrics=gov_metrics),
    )
    return base.render(
        report=ctx,
        env_html=env_html,
        soc_html=soc_html,
        gov_html=gov_html,
    )
