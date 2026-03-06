with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fresh Mind Light Theme
replacements = [
    # Root variables
    ('--bg-primary: #0F1A14;', '--bg-primary: #F6FBF7;'),
    ('--bg-secondary: #152420;', '--bg-secondary: #FFFFFF;'),
    ('--bg-card: #1C2E26;', '--bg-card: #F5FAF6;'),
    ('--bg-card-hover: #243830;', '--bg-card-hover: #E8F5E9;'),
    ('--accent: #5ABB8A;', '--accent: #4CAF50;'),
    ('--accent-light: #78D4A4;', '--accent-light: #81C784;'),
    ('--accent-glow: rgba(90, 187, 138, 0.25);', '--accent-glow: rgba(76, 175, 80, 0.15);'),
    ('--text-primary: #E4F0EA;', '--text-primary: #1B5E20;'),
    ('--text-secondary: #9EB8A8;', '--text-secondary: #558B2F;'),
    ('--text-muted: #5F7A6A;', '--text-muted: #9CCC65;'),
    ('--success: #5ABB8A;', '--success: #4CAF50;'),
    ('--warning: #D4B44C;', '--warning: #FBC02D;'),
    ('--danger: #C85A5A;', '--danger: #E53935;'),
    ('--border: #2A4038;', '--border: #C5E1A5;'),
    ('--pro-bg: rgba(90, 187, 138, 0.08);', '--pro-bg: rgba(76, 175, 80, 0.08);'),
    ('--con-bg: rgba(200, 90, 90, 0.08);', '--con-bg: rgba(229, 57, 53, 0.08);'),
    ('--pro-border: rgba(90, 187, 138, 0.3);', '--pro-border: rgba(76, 175, 80, 0.3);'),
    ('--con-border: rgba(200, 90, 90, 0.3);', '--con-border: rgba(229, 57, 53, 0.3);'),
    # Card colors
    ('--card1: #5ABB8A;', '--card1: #4CAF50;'),
    ('--card1-light: #78D4A4;', '--card1-light: #81C784;'),
    ('--card1-glow: rgba(90, 187, 138, 0.15);', '--card1-glow: rgba(76, 175, 80, 0.12);'),
    ('--card2: #4AA8B8;', '--card2: #66BB6A;'),
    ('--card2-light: #68C0D0;', '--card2-light: #81C784;'),
    ('--card2-glow: rgba(74, 168, 184, 0.15);', '--card2-glow: rgba(102, 187, 106, 0.12);'),
    ('--card3: #A8BB5A;', '--card3: #81C784;'),
    ('--card3-light: #C0D478;', '--card3-light: #A5D6A7;'),
    ('--card3-glow: rgba(168, 187, 90, 0.15);', '--card3-glow: rgba(129, 199, 132, 0.12);'),
    ('--card4: #5A8ABB;', '--card4: #A5D6A7;'),
    ('--card4-light: #78A4D4;', '--card4-light: #C8E6C9;'),
    ('--card4-glow: rgba(90, 138, 187, 0.15);', '--card4-glow: rgba(165, 214, 167, 0.12);'),
    ('--card5: #8A9E70;', '--card5: #C8E6C9;'),
    ('--card5-light: #A2B688;', '--card5-light: #E8F5E9;'),
    ('--card5-glow: rgba(138, 158, 112, 0.15);', '--card5-glow: rgba(200, 230, 201, 0.12);'),
    # Button text color (hardcoded for light bg)
    ('color: #0F1A14;', 'color: #FFFFFF;'),
    # RGBA for primary green
    ('rgba(90, 187, 138,', 'rgba(76, 175, 80,'),
    ('rgba(74, 168, 184,', 'rgba(102, 187, 106,'),
    ('rgba(168, 187, 90,', 'rgba(129, 199, 132,'),
    ('rgba(90, 138, 187,', 'rgba(165, 214, 167,'),
    ('rgba(138, 158, 112,', 'rgba(200, 230, 201,'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fresh Mind theme applied!')
