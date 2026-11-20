import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "generated_resumes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    s = re.sub(r'[\\/*?:"<>|]', "", name)
    s = re.sub(r'\s+', "_", s)
    return s[:60]

def add_section_heading(doc: docx.Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(text.upper())
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(11.5)
    run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy / ATS Blue
    
    # Add bottom border to heading paragraph
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '94A3B8')
    pBdr.append(bottom)
    pPr.append(pBdr)

def generate_resume_docx(resume_data: Dict[str, Any], filename_prefix: str = "Resume") -> str:
    """
    Generates an ATS-compliant Word (.docx) document from structured resume data.
    Returns the absolute path of the generated .docx file.
    """
    doc = docx.Document()

    # Set page margins to standard 0.75 inches for optimal ATS and readability
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    contact = resume_data.get("contact", {})
    name = contact.get("name", resume_data.get("full_name", "Candidate")).strip() or "Candidate"
    
    # Header: Candidate Name
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_before = Pt(0)
    p_name.paragraph_format.space_after = Pt(2)
    run_name = p_name.add_run(name.upper())
    run_name.bold = True
    run_name.font.name = "Calibri"
    run_name.font.size = Pt(18)
    run_name.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle / Contact Info
    contact_items = []
    if contact.get("location"):
        contact_items.append(contact["location"])
    if contact.get("phone"):
        contact_items.append(contact["phone"])
    if contact.get("email"):
        contact_items.append(contact["email"])
    if contact.get("linkedin"):
        contact_items.append(contact["linkedin"])
    if contact.get("github"):
        contact_items.append(contact["github"])

    if contact_items:
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(10)
        run_sub = p_sub.add_run("  |  ".join(contact_items))
        run_sub.font.name = "Calibri"
        run_sub.font.size = Pt(9.5)
        run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Professional Summary
    summary = resume_data.get("summary", "").strip()
    if summary:
        add_section_heading(doc, "Professional Summary")
        p_sum = doc.add_paragraph()
        p_sum.paragraph_format.space_before = Pt(2)
        p_sum.paragraph_format.space_after = Pt(6)
        p_sum.paragraph_format.line_spacing = 1.15
        run_sum = p_sum.add_run(summary)
        run_sum.font.name = "Calibri"
        run_sum.font.size = Pt(10)
        run_sum.font.color.rgb = RGBColor(30, 41, 59)

    # Technical Skills / Core Competencies
    skills = resume_data.get("skills", {})
    if skills:
        add_section_heading(doc, "Core Competencies & Technical Skills")
        if isinstance(skills, dict):
            for cat_name, skill_list in skills.items():
                if not skill_list:
                    continue
                p_sk = doc.add_paragraph()
                p_sk.paragraph_format.space_before = Pt(1)
                p_sk.paragraph_format.space_after = Pt(2)
                p_sk.paragraph_format.line_spacing = 1.1
                
                run_cat = p_sk.add_run(f"{cat_name}: ")
                run_cat.bold = True
                run_cat.font.name = "Calibri"
                run_cat.font.size = Pt(9.5)
                run_cat.font.color.rgb = RGBColor(15, 23, 42)

                s_str = ", ".join(skill_list) if isinstance(skill_list, list) else str(skill_list)
                run_items = p_sk.add_run(s_str)
                run_items.font.name = "Calibri"
                run_items.font.size = Pt(9.5)
                run_items.font.color.rgb = RGBColor(51, 65, 85)
        elif isinstance(skills, list):
            p_sk = doc.add_paragraph()
            p_sk.paragraph_format.space_before = Pt(1)
            p_sk.paragraph_format.space_after = Pt(2)
            run_items = p_sk.add_run(", ".join(skills))
            run_items.font.name = "Calibri"
            run_items.font.size = Pt(9.5)
            run_items.font.color.rgb = RGBColor(51, 65, 85)

    # Professional Experience
    experiences = resume_data.get("experiences", resume_data.get("work_experience", []))
    if experiences:
        add_section_heading(doc, "Professional Experience")
        for exp in experiences:
            p_role = doc.add_paragraph()
            p_role.paragraph_format.space_before = Pt(5)
            p_role.paragraph_format.space_after = Pt(1)
            p_role.paragraph_format.keep_with_next = True

            role_title = exp.get("title", "Role").strip()
            company = exp.get("company", "Company").strip()
            loc = exp.get("location", "").strip()
            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}".strip(" -")

            run_title = p_role.add_run(role_title)
            run_title.bold = True
            run_title.font.name = "Calibri"
            run_title.font.size = Pt(10.5)
            run_title.font.color.rgb = RGBColor(15, 23, 42)

            if company:
                run_comp = p_role.add_run(f" | {company}")
                run_comp.font.name = "Calibri"
                run_comp.font.size = Pt(10.5)
                run_comp.font.color.rgb = RGBColor(51, 65, 85)

            meta_parts = [p for p in [loc, dates] if p]
            if meta_parts:
                run_meta = p_role.add_run(f" ({' | '.join(meta_parts)})")
                run_meta.italic = True
                run_meta.font.name = "Calibri"
                run_meta.font.size = Pt(9.5)
                run_meta.font.color.rgb = RGBColor(100, 116, 139)

            # Bullets
            for bullet in exp.get("bullets", []):
                p_b = doc.add_paragraph(style='List Bullet')
                p_b.paragraph_format.space_before = Pt(0)
                p_b.paragraph_format.space_after = Pt(2)
                p_b.paragraph_format.line_spacing = 1.15
                
                clean_bullet = re.sub(r'^[•\-\*]\s*', '', bullet).strip()
                run_b = p_b.add_run(clean_bullet)
                run_b.font.name = "Calibri"
                run_b.font.size = Pt(9.5)
                run_b.font.color.rgb = RGBColor(30, 41, 59)

    # Key Projects
    projects = resume_data.get("projects", [])
    if projects:
        add_section_heading(doc, "Key Projects & Technical Architectures")
        for proj in projects:
            p_proj = doc.add_paragraph()
            p_proj.paragraph_format.space_before = Pt(5)
            p_proj.paragraph_format.space_after = Pt(1)
            p_proj.paragraph_format.keep_with_next = True

            proj_name = proj.get("name", "Project").strip()
            org = proj.get("organisation", "").strip()
            org_dur = proj.get("organisation_duration", "").strip()
            tech_stack = proj.get("tech_stack", "").strip()

            run_pname = p_proj.add_run(proj_name)
            run_pname.bold = True
            run_pname.font.name = "Calibri"
            run_pname.font.size = Pt(10)
            run_pname.font.color.rgb = RGBColor(15, 23, 42)

            if org:
                org_label = f"  |  {org}"
                if org_dur:
                    org_label += f" ({org_dur})"
                run_org = p_proj.add_run(org_label)
                run_org.font.name = "Calibri"
                run_org.font.size = Pt(9.5)
                run_org.font.color.rgb = RGBColor(100, 116, 139)

            if tech_stack:
                run_stack = p_proj.add_run(f" [{tech_stack}]")
                run_stack.italic = True
                run_stack.font.name = "Calibri"
                run_stack.font.size = Pt(9)
                run_stack.font.color.rgb = RGBColor(79, 70, 229)

            if proj.get("description"):
                p_pdesc = doc.add_paragraph()
                p_pdesc.paragraph_format.space_before = Pt(0)
                p_pdesc.paragraph_format.space_after = Pt(2)
                run_desc = p_pdesc.add_run(proj["description"])
                run_desc.font.name = "Calibri"
                run_desc.font.size = Pt(9.5)
                run_desc.font.color.rgb = RGBColor(51, 65, 85)

            for bullet in proj.get("bullets", []):
                p_b = doc.add_paragraph(style='List Bullet')
                p_b.paragraph_format.space_before = Pt(0)
                p_b.paragraph_format.space_after = Pt(2)
                p_b.paragraph_format.line_spacing = 1.15
                clean_bullet = re.sub(r'^[•\-\*]\s*', '', bullet).strip()
                run_b = p_b.add_run(clean_bullet)
                run_b.font.name = "Calibri"
                run_b.font.size = Pt(9.5)
                run_b.font.color.rgb = RGBColor(30, 41, 59)

    # Education
    education = resume_data.get("education", [])
    if education:
        add_section_heading(doc, "Education")
        for edu in education:
            p_edu = doc.add_paragraph()
            p_edu.paragraph_format.space_before = Pt(3)
            p_edu.paragraph_format.space_after = Pt(1)
            
            degree = edu.get("degree", "").strip()
            inst = edu.get("institution", "").strip()
            yr = edu.get("year", "").strip()
            details = edu.get("details", "").strip()

            run_deg = p_edu.add_run(degree)
            run_deg.bold = True
            run_deg.font.name = "Calibri"
            run_deg.font.size = Pt(10)
            run_deg.font.color.rgb = RGBColor(15, 23, 42)

            if inst:
                run_inst = p_edu.add_run(f" | {inst}")
                run_inst.font.name = "Calibri"
                run_inst.font.size = Pt(10)
                run_inst.font.color.rgb = RGBColor(51, 65, 85)

            if yr:
                run_yr = p_edu.add_run(f" ({yr})")
                run_yr.italic = True
                run_yr.font.name = "Calibri"
                run_yr.font.size = Pt(9.5)
                run_yr.font.color.rgb = RGBColor(100, 116, 139)

            if details:
                p_edet = doc.add_paragraph()
                p_edet.paragraph_format.space_before = Pt(0)
                p_edet.paragraph_format.space_after = Pt(2)
                run_det = p_edet.add_run(details)
                run_det.font.name = "Calibri"
                run_det.font.size = Pt(9)
                run_det.font.color.rgb = RGBColor(71, 85, 105)

    # Certifications
    certs = resume_data.get("certifications", [])
    if certs:
        add_section_heading(doc, "Certifications")
        for c in certs:
            p_c = doc.add_paragraph(style='List Bullet')
            p_c.paragraph_format.space_before = Pt(0)
            p_c.paragraph_format.space_after = Pt(2)
            c_text = c if isinstance(c, str) else c.get("name", str(c))
            run_c = p_c.add_run(c_text)
            run_c.font.name = "Calibri"
            run_c.font.size = Pt(9.5)
            run_c.font.color.rgb = RGBColor(30, 41, 59)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_prefix = sanitize_filename(filename_prefix)
    filename = f"{clean_prefix}_{timestamp}.docx"
    file_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(file_path)

    # Also save matching .txt plain file
    txt_filename = f"{clean_prefix}_{timestamp}.txt"
    txt_path = os.path.join(OUTPUT_DIR, txt_filename)
    plain_text = generate_plain_text(resume_data)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(plain_text)

    return file_path

def generate_plain_text(resume_data: Dict[str, Any]) -> str:
    lines = []
    contact = resume_data.get("contact", {})
    name = contact.get("name", resume_data.get("full_name", "CANDIDATE")).strip() or "CANDIDATE"
    lines.append(name.upper())

    contact_items = []
    if contact.get("location"):
        contact_items.append(contact["location"])
    if contact.get("phone"):
        contact_items.append(contact["phone"])
    if contact.get("email"):
        contact_items.append(contact["email"])
    if contact.get("linkedin"):
        contact_items.append(contact["linkedin"])
    if contact.get("github"):
        contact_items.append(contact["github"])
    if contact_items:
        lines.append(" | ".join(contact_items))
    lines.append("")

    summary = resume_data.get("summary", "").strip()
    if summary:
        lines.append("PROFESSIONAL SUMMARY")
        lines.append(summary)
        lines.append("")

    skills = resume_data.get("skills", {})
    if skills:
        lines.append("CORE COMPETENCIES & TECHNICAL SKILLS")
        if isinstance(skills, dict):
            for cat, s_list in skills.items():
                s_str = ", ".join(s_list) if isinstance(s_list, list) else str(s_list)
                lines.append(f"{cat}: {s_str}")
        elif isinstance(skills, list):
            lines.append(", ".join(skills))
        lines.append("")

    experiences = resume_data.get("experiences", resume_data.get("work_experience", []))
    if experiences:
        lines.append("PROFESSIONAL EXPERIENCE")
        for exp in experiences:
            header = f"{exp.get('title', '')} | {exp.get('company', '')} | {exp.get('location', '')} | {exp.get('start_date', '')} - {exp.get('end_date', '')}"
            lines.append(header)
            for b in exp.get("bullets", []):
                clean_b = re.sub(r'^[•\-\*]\s*', '', b).strip()
                lines.append(f"- {clean_b}")
            lines.append("")

    projects = resume_data.get("projects", [])
    if projects:
        lines.append("KEY PROJECTS & ARCHITECTURES")
        for proj in projects:
            proj_header_parts = [proj.get('name', '')]
            org = proj.get("organisation", "").strip()
            org_dur = proj.get("organisation_duration", "").strip()
            if org and org_dur:
                proj_header_parts.append(f"{org} ({org_dur})")
            elif org:
                proj_header_parts.append(org)
            if proj.get('tech_stack'):
                proj_header_parts.append(f"[{proj.get('tech_stack')}]")
            lines.append(" | ".join(proj_header_parts))
            if proj.get("description"):
                lines.append(f"Description: {proj.get('description')}")
            for b in proj.get("bullets", []):
                clean_b = re.sub(r'^[•\-\*]\s*', '', b).strip()
                lines.append(f"- {clean_b}")
            lines.append("")

    education = resume_data.get("education", [])
    if education:
        lines.append("EDUCATION")
        for edu in education:
            lines.append(f"{edu.get('degree', '')} | {edu.get('institution', '')} ({edu.get('year', '')})")
            if edu.get("details"):
                lines.append(f"  {edu.get('details')}")
        lines.append("")

    certs = resume_data.get("certifications", [])
    if certs:
        lines.append("CERTIFICATIONS")
        for c in certs:
            c_text = c if isinstance(c, str) else c.get("name", str(c))
            lines.append(f"- {c_text}")

    return "\n".join(lines).strip()
