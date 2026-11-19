import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Non-interactive backend
import matplotlib
matplotlib.use('Agg')

def draw_frame_system(ax, l, h, q=0.0, H=0.0, title="Statisches System"):
    """
    Zeichnet das Rahmensystem mit biegesteifen Ecken (ohne Gelenkkreise an den Rahmenknoten),
    Stäben, Lagern, Bemaßung und Lasten.
    """
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=11, fontweight='bold', pad=12, color='#111111')
    
    # Axes limits
    ax.set_xlim(-1.6, l + 1.6)
    ax.set_ylim(-1.6, h + 2.2)
    
    # Frame geometry - biegesteifer Rahmen (durchgehende Ecken)
    ax.plot([0, 0, l, l], [0, h, h, 0], color='#111111', lw=3.2, zorder=3)
    
    # Node numbers (1, 2, 3, 4) - OHNE Kreise/Scatter-Punkte an den biegesteifen Rahmenknoten
    nodes = [(0, 0, '1', (0.35, 0.35)),
             (0, h, '2', (0.35, -0.35)),
             (l, h, '3', (-0.35, -0.35)),
             (l, 0, '4', (-0.35, 0.35))]
             
    for nx, ny, nlab, (off_x, off_y) in nodes:
        ax.text(nx + off_x, ny + off_y, f"({nlab})", fontsize=10, fontweight='bold', 
                color='#333333', ha='center', va='center', zorder=6)
                
    # Element labels ①, ②, ③
    ax.text(-0.35, h/2, "①", fontsize=11, color='#004488', fontweight='bold', ha='center', va='center')
    ax.text(l/2, h+0.35, "②", fontsize=11, color='#004488', fontweight='bold', ha='center', va='center')
    ax.text(l+0.35, h/2, "③", fontsize=11, color='#004488', fontweight='bold', ha='center', va='center')
    
    # Hinged Support triangles
    for sx in [0, l]:
        tri = np.array([[sx, 0], [sx-0.22, -0.38], [sx+0.22, -0.38]])
        ax.add_patch(patches.Polygon(tri, closed=True, facecolor='#E8E8E8', edgecolor='#111111', lw=1.5, zorder=4))
        ax.plot([sx-0.32, sx+0.32], [-0.38, -0.38], color='#111111', lw=2, zorder=4)
        for hx in np.linspace(sx-0.30, sx+0.24, 6):
            ax.plot([hx, hx-0.08], [-0.38, -0.52], color='#111111', lw=1.2, zorder=4)
            
    # Dimensioning lines
    # Length l
    ax0_y = -0.85
    ax.plot([0, l], [ax0_y, ax0_y], color='#666666', lw=1.0, ls='--')
    ax.text(l/2, ax0_y - 0.28, f"$l = {l:.2f}\\text{{ m}}$", fontsize=9, ha='center', color='#444444')
    ax.plot([0, 0], [0, ax0_y-0.1], color='#888888', lw=0.8, ls=':')
    ax.plot([l, l], [0, ax0_y-0.1], color='#888888', lw=0.8, ls=':')
    
    # Height h
    ax0_x = -1.0
    ax.plot([ax0_x, ax0_x], [0, h], color='#666666', lw=1.0, ls='--')
    ax.text(ax0_x - 0.35, h/2, f"$h = {h:.2f}\\text{{ m}}$", fontsize=9, va='center', rotation=90, color='#444444')
    ax.plot([0, ax0_x-0.1], [0, 0], color='#888888', lw=0.8, ls=':')
    ax.plot([0, ax0_x-0.1], [h, h], color='#888888', lw=0.8, ls=':')


def plot_diagram_single(ax, l, h, data_dict, diag_type='M', title=None, scale_fac=1.0, show_values=True, show_reactions=True):
    """
    Zeichnet ein einzelnes Schnittgrößendiagramm (M, V oder N) mit präziser Schraffur,
    nummerischen Werte-Boxen und Auflagerreaktionen.
    """
    q, H = data_dict['q'], data_dict['H']
    reactions = data_dict['reactions']
    z_c1, x_b, z_c2 = data_dict['z_col1'], data_dict['x_beam'], data_dict['z_col2']
    
    if diag_type == 'M':
        d1, d2, d3 = data_dict['M_col1'], data_dict['M_beam'], data_dict['M_col2']
        color_main, color_fill = '#003399', '#D6E4FF'
        unit = "kNm"
        diag_title = title or "Biegemoment M [kNm]"
        default_scale = 0.075 * scale_fac
    elif diag_type == 'V':
        d1, d2, d3 = data_dict['V_col1'], data_dict['V_beam'], data_dict['V_col2']
        color_main, color_fill = '#008055', '#E0F4EE'
        unit = "kN"
        diag_title = title or "Querkraft V [kN]"
        default_scale = 0.05 * scale_fac
    else: # 'N'
        d1, d2, d3 = data_dict['N_col1'], data_dict['N_beam'], data_dict['N_col2']
        color_main, color_fill = '#CC0000', '#FFEAEA'
        unit = "kN"
        diag_title = title or "Normalkraft N [kN]"
        default_scale = 0.045 * scale_fac
        
    draw_frame_system(ax, l, h, q, H, diag_title)
    
    scale = default_scale
    
    # 1. Linker Stiel (Stab 1)
    x_c1 = - d1 * scale
    y_c1 = z_c1
    poly_c1_x = np.concatenate([[0], x_c1, [0]])
    poly_c1_y = np.concatenate([[0], y_c1, [h]])
    ax.fill(poly_c1_x, poly_c1_y, color=color_fill, alpha=0.65, zorder=2)
    ax.plot(x_c1, y_c1, color=color_main, lw=2.2, zorder=3)
    
    # 2. Riegel (Stab 2)
    x_b_plot = x_b
    y_b_plot = h - d2 * scale
    poly_b_x = np.concatenate([[0], x_b_plot, [l]])
    poly_b_y = np.concatenate([[h], y_b_plot, [h]])
    ax.fill(poly_b_x, poly_b_y, color=color_fill, alpha=0.65, zorder=2)
    ax.plot(x_b_plot, y_b_plot, color=color_main, lw=2.2, zorder=3)
    
    # 3. Rechter Stiel (Stab 3)
    x_c2 = l + d3 * scale
    y_c2 = z_c2
    poly_c2_x = np.concatenate([[l], x_c2, [l]])
    poly_c2_y = np.concatenate([[0], y_c2, [h]])
    ax.fill(poly_c2_x, poly_c2_y, color=color_fill, alpha=0.65, zorder=2)
    ax.plot(x_c2, y_c2, color=color_main, lw=2.2, zorder=3)
    
    # Orthogonale Schraffurlinien
    n_hatch = 22
    for hx in np.linspace(0.15, l-0.15, n_hatch):
        val_h = np.interp(hx, x_b, d2)
        hy = h - val_h * scale
        ax.plot([hx, hx], [h, hy], color=color_main, lw=0.6, alpha=0.5, zorder=2)
        
    for hy in np.linspace(0.1, h-0.1, 12):
        val_h = np.interp(hy, z_c1, d1)
        hx = - val_h * scale
        ax.plot([0, hx], [hy, hy], color=color_main, lw=0.6, alpha=0.5, zorder=2)
        
    for hy in np.linspace(0.1, h-0.1, 12):
        val_h = np.interp(hy, z_c2, d3)
        hx = l + val_h * scale
        ax.plot([l, hx], [hy, hy], color=color_main, lw=0.6, alpha=0.5, zorder=2)
        
    # NUMMERISCHE WERTE-BOXEN
    if show_values:
        def draw_val_label(px, py, text_str, align_x='center', align_y='center', bg="#FFFFFF"):
            ax.text(px, py, text_str, fontsize=9.0, fontweight='bold', color=color_main,
                    ha=align_x, va=align_y, zorder=7,
                    bbox=dict(boxstyle="round,pad=0.25", facecolor=bg, edgecolor=color_main, lw=1.2))

        # Eckmoment links (Knoten 2)
        val_c1_top = d1[-1]
        if abs(val_c1_top) > 0.05:
            box_x = -0.35 if val_c1_top > 0 else -0.30
            draw_val_label(box_x, h + 0.25, f"{val_c1_top:.2f}", 'right', 'bottom')
            
        # Eckmoment rechts (Knoten 3)
        val_c2_top = d3[-1]
        if abs(val_c2_top) > 0.05:
            box_x = l + 0.35 if val_c2_top > 0 else l + 0.30
            draw_val_label(box_x, h + 0.25, f"{val_c2_top:.2f}", 'left', 'bottom')
            
        # Max. Feldmoment im Riegel
        idx_ext = np.argmax(np.abs(d2))
        val_ext = d2[idx_ext]
        x_ext = x_b[idx_ext]
        y_ext = y_b_plot[idx_ext]
        
        if abs(val_ext) > 0.05:
            offset_y = -0.38 if val_ext > 0 else +0.38
            draw_val_label(x_ext, y_ext + offset_y, f"{val_ext:.2f} {unit}", 'center', 'center')

        # Vorzeichen-Badges (+ / -) bei V und N
        if diag_type in ['V', 'N']:
            val_mid_b = d2[len(d2)//2]
            sign_b = "+" if val_mid_b >= 0 else "-"
            if abs(val_mid_b) > 0.05:
                ax.text(l/2, h - (val_mid_b*scale)/2, f"({sign_b})", fontsize=10, fontweight='bold',
                        color=color_main, ha='center', va='center', zorder=6)
                        
            val_mid_c1 = d1[len(d1)//2]
            sign_c1 = "+" if val_mid_c1 >= 0 else "-"
            if abs(val_mid_c1) > 0.05:
                ax.text(-(val_mid_c1*scale)/2, h/2, f"({sign_c1})", fontsize=10, fontweight='bold',
                        color=color_main, ha='center', va='center', zorder=6)
                        
            val_mid_c2 = d3[len(d3)//2]
            sign_c2 = "+" if val_mid_c2 >= 0 else "-"
            if abs(val_mid_c2) > 0.05:
                ax.text(l + (val_mid_c2*scale)/2, h/2, f"({sign_c2})", fontsize=10, fontweight='bold',
                        color=color_main, ha='center', va='center', zorder=6)

    # AUFLAGERREAKTIONEN AN DEN KNOTEN 1 & 4
    if show_reactions:
        Ah, Av = reactions['Ah'], reactions['Av']
        Bh, Bv = reactions['Bh'], reactions['Bv']
        
        # Auflager A (Knoten 1)
        ax.annotate(f"$A_v = {Av:.2f}\\text{{ kN}}$", xy=(0, -0.4), xytext=(0, -1.4),
                    ha='center', va='top', fontsize=8.5, fontweight='bold', color='#111111',
                    arrowprops=dict(arrowstyle="->", color='#111111', lw=1.2))
                    
        ah_dir = 1 if Ah >= 0 else -1
        ax.annotate(f"$A_h = {abs(Ah):.2f}\\text{{ kN}}$", xy=(0, -0.2), xytext=(-1.1 * ah_dir, -0.2),
                    ha='right' if ah_dir > 0 else 'left', va='center', fontsize=8.5, fontweight='bold', color='#111111',
                    arrowprops=dict(arrowstyle="->", color='#111111', lw=1.2))

        # Auflager B (Knoten 4)
        ax.annotate(f"$B_v = {Bv:.2f}\\text{{ kN}}$", xy=(l, -0.4), xytext=(l, -1.4),
                    ha='center', va='top', fontsize=8.5, fontweight='bold', color='#111111',
                    arrowprops=dict(arrowstyle="->", color='#111111', lw=1.2))
                    
        bh_dir = 1 if Bh >= 0 else -1
        ax.annotate(f"$B_h = {abs(Bh):.2f}\\text{{ kN}}$", xy=(l, -0.2), xytext=(l + 1.1 * bh_dir, -0.2),
                    ha='left' if bh_dir > 0 else 'right', va='center', fontsize=8.5, fontweight='bold', color='#111111',
                    arrowprops=dict(arrowstyle="->", color='#111111', lw=1.2))


def create_full_figure(solver_obj, scale_fac=1.0, show_values=True):
    """
    Erstellt die 4-teilige Gesamtschau (System, M, V, N).
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10.5), dpi=150)
    fig.patch.set_facecolor('#FFFFFF')
    
    data = solver_obj.solve_case()
    l, h = solver_obj.l, solver_obj.h
    q, H = solver_obj.q, solver_obj.H
    
    # 1. System
    draw_frame_system(axes[0,0], l, h, q, H, "Statisches System & Belastung")
    if q > 0:
        y_q = h + 0.8
        axes[0,0].plot([0, l], [y_q, y_q], color='#0055AA', lw=1.5)
        for qx in np.linspace(0.2, l-0.2, 7):
            axes[0,0].annotate('', xy=(qx, h), xytext=(qx, y_q),
                               arrowprops=dict(arrowstyle="-|>", color='#0055AA', lw=1.5, mutation_scale=10))
        axes[0,0].text(l/2, y_q + 0.22, f"$q_k = {q:.2f}\\text{{ kN/m}}$", color='#0055AA', fontsize=10, fontweight='bold', ha='center')
        
    if H > 0:
        axes[0,0].annotate('', xy=(0, h), xytext=(-1.1, h),
                           arrowprops=dict(arrowstyle="-|>", color='#CC0000', lw=2.0, mutation_scale=12))
        axes[0,0].text(-0.8, h + 0.35, f"$H_{{w,k}} = {H:.2f}\\text{{ kN}}$", color='#CC0000', fontsize=10, fontweight='bold', ha='center')

    # 2. M
    plot_diagram_single(axes[0,1], l, h, data, 'M', "Biegemoment M [kNm]", scale_fac, show_values, show_reactions=True)
    
    # 3. V
    plot_diagram_single(axes[1,0], l, h, data, 'V', "Querkraft V [kN]", scale_fac, show_values, show_reactions=True)
    
    # 4. N
    plot_diagram_single(axes[1,1], l, h, data, 'N', "Normalkraft N [kN]", scale_fac, show_values, show_reactions=True)
    
    plt.tight_layout()
    return fig


def create_comparison_figure(solver_obj, scale_fac=1.0, show_values=True):
    """
    Erstellt die 3-teilige Gegenüberstellung der Momentenverläufe exakt wie in der Bildvorlage:
    a) Vertikallast q_k
    b) Horizontallast H_{w,k}
    c) Überlagerung (q_k + H_{w,k})
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.8), dpi=150)
    fig.patch.set_facecolor('#FFFFFF')
    
    l, h = solver_obj.l, solver_obj.h
    q, H = solver_obj.q, solver_obj.H
    
    # Lastfall a: nur q
    data_a = solver_obj.solve_case(q_val=q, H_val=0.0)
    plot_diagram_single(axes[0], l, h, data_a, 'M', f"a) Vertikallast $q_k = {q:.1f}\\text{{ kN/m}}$", scale_fac, show_values, show_reactions=True)
    
    # Lastfall b: nur H
    data_b = solver_obj.solve_case(q_val=0.0, H_val=H)
    plot_diagram_single(axes[1], l, h, data_b, 'M', f"b) Horizontallast $H_{{w,k}} = {H:.1f}\\text{{ kN}}$", scale_fac, show_values, show_reactions=True)
    
    # Lastfall c: Überlagerung
    data_c = solver_obj.solve_case(q_val=q, H_val=H)
    plot_diagram_single(axes[2], l, h, data_c, 'M', f"c) Überlagerung $(q_k + H_{{w,k}})$", scale_fac, show_values, show_reactions=True)
    
    plt.tight_layout()
    return fig
