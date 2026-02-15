from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.config import get_settings


def _project_export_dir(project_id: str) -> Path:
    settings = get_settings()
    export_dir = Path(settings.export_dir) / project_id
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def export_technical_pdf(project: dict, generation: dict) -> str:
    target = _project_export_dir(project["id"]) / f"plan_technique_{project['id']}.pdf"
    c = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 50, "ScaffoldPlan AI - Plan technique echafaudage")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Projet: {project['name']} ({project['id']})")
    c.drawString(40, height - 85, f"Date: {datetime.utcnow().isoformat()} UTC")
    c.drawString(40, height - 110, f"Facade: {generation.get('facade_width_m', 0)}m x {generation.get('facade_height_m', 0)}m")
    c.drawString(40, height - 125, f"Niveaux: {generation.get('levels', 0)}")
    c.drawString(40, height - 140, f"Travees: {generation.get('bay_layout_m', [])}")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 170, "Quantitatif principal")
    y = height - 190
    c.setFont("Helvetica", 9)
    for line in generation.get("quantities", [])[:26]:
        c.drawString(45, y, f"- {line['type']}: {line['quantity']} u. (stock: {line['in_stock']}, manque: {line['shortage']})")
        y -= 14
        if y < 90:
            c.showPage()
            y = height - 50

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 10, "Avertissements conformite")
    c.setFont("Helvetica", 9)
    y -= 30
    warnings = generation.get("warnings", [])
    if not warnings:
        c.drawString(45, y, "- Aucun avertissement.")
    else:
        for warning in warnings[:10]:
            c.drawString(45, y, f"- [{warning['severity'].upper()}] {warning['code']} - {warning['message']}")
            y -= 14
            if y < 70:
                c.showPage()
                y = height - 60

    c.save()
    return str(target)


def export_quantitative_excel(project: dict, generation: dict) -> str:
    target = _project_export_dir(project["id"]) / f"quantitatif_{project['id']}.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Quantitatif"
    ws.append(["Projet", project["name"]])
    ws.append(["ID", project["id"]])
    ws.append([])
    ws.append(["Type", "Quantite", "Poids unitaire (kg)", "Poids total (kg)", "Stock", "Manque"])
    for line in generation.get("quantities", []):
        ws.append(
            [
                line["type"],
                line["quantity"],
                line["unit_weight_kg"],
                line["total_weight_kg"],
                line["in_stock"],
                line["shortage"],
            ]
        )
    ws.append([])
    ws.append(["Poids total (kg)", generation.get("total_weight_kg", 0)])
    ws.append(["Volume camion estime (m3)", generation.get("total_volume_m3", 0)])
    wb.save(str(target))
    return str(target)


def export_delivery_note(project: dict, generation: dict) -> str:
    target = _project_export_dir(project["id"]) / f"bon_sortie_depot_{project['id']}.csv"
    lines = ["type,quantite,stock,manque"]
    for line in generation.get("quantities", []):
        lines.append(f"{line['type']},{line['quantity']},{line['in_stock']},{line['shortage']}")
    target.write_text("\n".join(lines), encoding="utf-8")
    return str(target)


def export_conformity_report(project: dict, generation: dict) -> str:
    target = _project_export_dir(project["id"]) / f"rapport_conformite_{project['id']}.pdf"
    c = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 50, "Rapport de conformite R408 - ScaffoldPlan AI")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Projet: {project['name']}")
    c.drawString(40, height - 85, f"Confiance generation: {generation.get('confidence', 0)}")
    c.drawString(40, height - 100, f"Validation requise: {'Oui' if generation.get('requires_confirmation') else 'Non'}")

    y = height - 130
    warnings = generation.get("warnings", [])
    if not warnings:
        c.drawString(45, y, "Aucune non-conformite detectee.")
    else:
        for warning in warnings:
            c.drawString(45, y, f"[{warning['severity'].upper()}] {warning['code']}")
            y -= 14
            c.drawString(55, y, warning["message"])
            y -= 20
            if y < 80:
                c.showPage()
                y = height - 50

    c.save()
    return str(target)
