from reportlab.lib.styles import ParagraphStyle


    #from reportlab.platypus import paragraph
normal = ParagraphStyle('normalna_czcionka',
                         fontSize=9,
                         #leading=1,
                         fontName='Arial',
                         alignment=0,)
right = ParagraphStyle('do_prawej',
                         fontSize=9,
                         #leading=1,
                         fontName='Arial',
                         alignment=2,)

bold = ParagraphStyle('pogrubiona_czcionka',
                         fontSize=9,
                         #leading=1,
                         fontName='Arial-Bold',
                         alignment=0,)

head = ParagraphStyle('naglowek_czcionka',
                         fontSize=12,
                         #leading=1,
                         fontName='Arial-Bold',
                         spaceAfter=6,
                         alignment=0,)

bold_center = ParagraphStyle('pogrubiona_wycentrowana_czcionka',
                         fontSize=9,
                         #leading=1,
                         fontName='Arial-Bold',
                         alignment=1,)

center = ParagraphStyle('wycentrowana_czcionka',
                         fontSize=9,
                         #leading=1,
                         fontName='Arial',
                         alignment=1,)

