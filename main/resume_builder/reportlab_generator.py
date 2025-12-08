from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from io import BytesIO
from typing import Dict, Any
import json 



def generate_resume_pdf(data: Dict[str, Any], image_data: bytes = None) -> BytesIO:
    # --- 1. Define Custom Styles ---
    styles = getSampleStyleSheet()

    # Header Styles (Left-aligned)
    styles.add(ParagraphStyle(
        'NameHeader', 
        parent=styles['Heading1'],
        fontSize=26,
        alignment=0, # Left-aligned
        spaceAfter=0.05 * inch,
    ))

    # Contact Info/Body Style
    styles.add(ParagraphStyle(
        'CustomBodyText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=0, # Left
        spaceAfter=1,
    ))

    # Section Title (Bolded, Bordered)
    styles.add(ParagraphStyle(
        'SectionTitle',
        parent=styles['h2'],
        fontSize=14,
        textColor=black,
        spaceAfter=0.05 * inch,
        borderPadding=2,
        borderWidth=1,
        borderColor=black,
    ))

    # Bullet Style (Standard for all lists)
    styles.add(ParagraphStyle(
        'BulletStyle',
        parent=styles['Bullet'],
        fontSize=10,
        leftIndent=0.25 * inch,
        spaceBefore=1,
        spaceAfter=1,
    ))
    
    # --- 2. Document Setup ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=0.75 * inch, 
        rightMargin=0.75 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    Story = []

    # --- 3. Header, Image, and Summary (Use Table for Layout) ---
    name = data.get('name', 'JUAN DELA CRUZ - RESUME')
    email = data.get('email', 'juan.dela.cruz@example.com')
    phone = data.get('phone', '+639XX-XXX-XXXX')
    address = data.get('address', 'Manila, Philippines')
    summary = data.get('summary', 'Dedicated professional ready for new challenges.')

    # Prepare Name and Summary paragraphs
    name_para = Paragraph(name.upper(), styles['NameHeader'])
    summary_para = Paragraph(summary, styles['CustomBodyText'])

    # Prepare Image (Max size 1 inch x 1 inch)
    if image_data:
        profile_image = Image(BytesIO(image_data), width=1*inch, height=1*inch)
    else:
        profile_image = Spacer(1, 1*inch) 
    
    # Create the top section using a two-column table
    top_content = Table(
        [
            [name_para, profile_image],
            [summary_para, '']
        ],
        colWidths=[5.5 * inch, 1.5 * inch],
        rowHeights=[None, None]
    )

    top_content.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'), # Align image to the right
    ]))

    Story.append(top_content)
    Story.append(Spacer(1, 0.25 * inch)) 

    # CONTACT Section 
    Story.append(Paragraph("PERSONAL INFORMATION", styles['SectionTitle']))
    Story.append(Paragraph(f"<b>ADDRESS:</b> {address}", styles['CustomBodyText']))
    Story.append(Paragraph(f"<b>PHONE NUMBER:</b> {phone}", styles['CustomBodyText']))
    Story.append(Paragraph(f"<b>EMAIL:</b> {email}", styles['CustomBodyText']))
    Story.append(Spacer(1, 0.25 * inch))

    # --- 4. Education ---
    Story.append(Paragraph("EDUCATION", styles['SectionTitle']))
    Story.append(Paragraph(f"<b>DEGREE/CERTIFICATE:</b> {data.get('edu_degree', 'Missing')}", styles['CustomBodyText']))
    Story.append(Paragraph(f"<b>UNIVERSITY NAME:</b> {data.get('edu_institution', 'Missing')}", styles['CustomBodyText']))
    Story.append(Paragraph(f"<b>LOCATION:</b> {data.get('edu_location', 'Missing')}", styles['CustomBodyText']))
    Story.append(Paragraph(f"<b>GRADUATION YEAR/DATE:</b> {data.get('edu_year', 'Missing')}", styles['CustomBodyText']))
    Story.append(Spacer(1, 0.25 * inch))


    # --- 5. Experience (With JSON parsing for bullets) ---
    Story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionTitle']))
    
    exp_titles = data.get('exp_titles', [])
    num_jobs = len(exp_titles)

    for i in range(num_jobs):
        try:
            title = exp_titles[i].strip()
            company = data['exp_companies'][i]
            dates = data['exp_dates'][i]
            location = data['exp_locations'][i]
            
            if not title:
                continue 

            Story.append(Paragraph(f"<b>{title}</b>", styles['CustomBodyText']))
            Story.append(Paragraph(f"<b>Company:</b> {company}", styles['CustomBodyText']))
            Story.append(Paragraph(f"<b>Date Worked:</b> {dates}", styles['CustomBodyText']))
            Story.append(Paragraph(f"<b>Location:</b> {location}", styles['CustomBodyText']))

            Story.append(Paragraph("<b>KEY ACHIEVEMENTS</b>", styles['CustomBodyText']))
            
            # Correct key: 'exp_bullets_json'
            bullets_json_string = data.get('exp_bullets_json', [])[i]
            bullets_list = []
            
            if bullets_json_string:
                try:
                    # Attempt to parse the JSON string into a Python list
                    bullets_list = json.loads(bullets_json_string)
                except (json.JSONDecodeError, TypeError):
                    # Fallback if the input is just plain text
                    bullets_list = [bullets_json_string]
            
            # Generate Bullet Points
            bullet_items = []
            for bullet in bullets_list:
                if isinstance(bullet, str) and bullet.strip():
                    bullet_items.append(ListItem(Paragraph(bullet.strip(), styles['BulletStyle'])))

            if bullet_items:
                Story.append(ListFlowable(
                    bullet_items,
                    bulletType='bullet',
                    start='bulletchar',
                    bulletAlign='left',
                    leftIndent=0.25 * inch, 
                    spaceAfter=0.1 * inch 
                ))
            
            Story.append(Spacer(1, 0.15 * inch))
            
        except IndexError:
            continue
    
    
    # --- 6. Skills ---
    Story.append(Paragraph("SKILLS", styles['SectionTitle']))
    
    all_skills = []
    
    # Collect all skills from all three categories into one list
    skill_data_keys = ['skill_category_1', 'skill_category_2', 'skill_category_3']
    for data_key in skill_data_keys:
        skill_string = data.get(data_key, '')
        if skill_string.strip():
            skills_list = [s.strip() for s in skill_string.split(',') if s.strip()]
            all_skills.extend(skills_list)
            
    if all_skills:
        skill_bullet_items = []
        for skill in all_skills:
            skill_bullet_items.append(ListItem(Paragraph(skill, styles['BulletStyle'])))

        Story.append(ListFlowable(
            skill_bullet_items,
            bulletType='bullet',
            start='bulletchar',
            bulletAlign='left',
            leftIndent=0.25 * inch, 
            spaceAfter=0.1 * inch 
        ))
        Story.append(Spacer(1, 0.25 * inch))


    # --- 7. Languages Spoken and 8. Interests ---
    
    list_sections = [
        ("LANGUAGES SPOKEN", [data.get(f'language_{i}', '') for i in range(1, 4)]),
        ("INTERESTS/ACTIVITIES", [data.get(f'interest_{i}', '') for i in range(1, 4)]),
    ]

    for title, items in list_sections:
        valid_items = [item.strip() for item in items if item and item.strip()]
        
        if valid_items:
            Story.append(Paragraph(title, styles['SectionTitle']))
            
            bullet_items = []
            for item in valid_items:
                bullet_items.append(ListItem(Paragraph(item, styles['BulletStyle'])))

            Story.append(ListFlowable(
                bullet_items,
                bulletType='bullet',
                start='bulletchar',
                bulletAlign='left',
                leftIndent=0.25 * inch, 
                spaceAfter=0.1 * inch 
            ))
            Story.append(Spacer(1, 0.25 * inch))


    # --- 9. Build Document ---
    doc.build(Story)
    buffer.seek(0)

    return buffer
