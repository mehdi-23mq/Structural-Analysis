import numpy as np

class PortalFrameSolver:
    """
    Exakter analytischer und numerischer Löser für 2D-Einfeldrahmen unter Vertikal- (q) und Horizontal- (H) Lasten.
    Unterstützt Zweigelenkrahmen, Dreigelenkrahmen und Eingespannte Rahmen.
    """
    def __init__(self, l=5.0, h=3.0, q=8.4, H=5.0, EI_R=1.0, EI_S=1.0, system_type="Zweigelenkrahmen"):
        self.l = float(l)
        self.h = float(h)
        self.q = float(q)
        self.H = float(H)
        self.EI_R = float(EI_R)
        self.EI_S = float(EI_S)
        self.system_type = system_type
        
        # Steifigkeitsverhältnis
        self.k = (self.EI_R / self.EI_S) * (self.h / self.l)
        
    def solve_case(self, q_val=None, H_val=None):
        """
        Berechnet einen spezifischen Lastfall (q_val, H_val).
        """
        q = self.q if q_val is None else float(q_val)
        H = self.H if H_val is None else float(H_val)
        
        l, h, k = self.l, self.h, self.k
        
        if self.system_type == "Zweigelenkrahmen":
            denom = 1.0 + (2.0/3.0) * k
            # Horizontaler Schub infolge q
            H_q = (q * l**2) / (12.0 * h * denom) if q != 0 else 0.0
            
            Ah_q = H_q
            Bh_q = -H_q
            Av_q = q * l / 2.0
            Bv_q = q * l / 2.0
            
            # Reaktionen infolge H
            Ah_H = - H / 2.0 if H != 0 else 0.0
            Bh_H = - H / 2.0 if H != 0 else 0.0
            Av_H = - H * h / l if H != 0 else 0.0
            Bv_H = H * h / l if H != 0 else 0.0
            
            # Superposition
            Ah = Ah_q + Ah_H
            Bh = Bh_q + Bh_H
            Av = Av_q + Av_H
            Bv = Bv_q + Bv_H
            
        elif self.system_type == "Dreigelenkrahmen":
            Ah_q = (q * l**2) / (8.0 * h) if q != 0 else 0.0
            Bh_q = -Ah_q
            Av_q = q * l / 2.0
            Bv_q = q * l / 2.0
            
            Ah_H = - H / 2.0
            Bh_H = - H / 2.0
            Av_H = - H * h / l
            Bv_H = H * h / l
            
            Ah = Ah_q + Ah_H
            Bh = Bh_q + Bh_H
            Av = Av_q + Av_H
            Bv = Bv_q + Bv_H
            
        else: # Eingespannter Rahmen
            Ah_q = (q * l**2) / (12.0 * h * (1.0 + k/6.0)) if q != 0 else 0.0
            Bh_q = -Ah_q
            Av_q = q * l / 2.0
            Bv_q = q * l / 2.0
            
            Ah_H = - H / 2.0
            Bh_H = - H / 2.0
            Av_H = - H * h / l
            Bv_H = H * h / l
            
            Ah = Ah_q + Ah_H
            Bh = Bh_q + Bh_H
            Av = Av_q + Av_H
            Bv = Bv_q + Bv_H
            
        # Diskrete Punkte entlang der Stäbe
        n_pts = 200
        z_col1 = np.linspace(0, h, n_pts) # Knoten 1 (0,0) -> Knoten 2 (0,h)
        x_beam = np.linspace(0, l, n_pts) # Knoten 2 (0,h) -> Knoten 3 (l,h)
        z_col2 = np.linspace(0, h, n_pts) # Knoten 4 (l,0) -> Knoten 3 (l,h)
        
        # Stiel links
        M_col1 = - Ah * z_col1
        V_col1 = np.full_like(z_col1, -Ah)
        N_col1 = np.full_like(z_col1, -Av)
        
        # Riegel
        M_corner1 = M_col1[-1]
        M_beam = M_corner1 + Av * x_beam - q * x_beam**2 / 2.0
        V_beam = Av - q * x_beam
        N_beam = np.full_like(x_beam, - (Ah + H))
        
        # Stiel rechts
        M_col2 = Bh * z_col2
        V_col2 = np.full_like(z_col2, Bh)
        N_col2 = np.full_like(z_col2, -Bv)
        
        # Kennwerte
        M1 = M_col1[-1]
        M2 = M_col2[-1]
        
        if q > 0:
            x_max = Av / q
            if 0 <= x_max <= l:
                M_max_beam = M_corner1 + Av * x_max - q * x_max**2 / 2.0
            else:
                x_max = 0.0 if abs(M_corner1) > abs(M_beam[-1]) else l
                M_max_beam = M_corner1 if abs(M_corner1) > abs(M_beam[-1]) else M_beam[-1]
        else:
            x_max = 0.0
            M_max_beam = M_corner1
            
        return {
            'q': q, 'H': H,
            'reactions': {'Ah': Ah, 'Av': Av, 'Bh': Bh, 'Bv': Bv},
            'z_col1': z_col1, 'x_beam': x_beam, 'z_col2': z_col2,
            'M_col1': M_col1, 'M_beam': M_beam, 'M_col2': M_col2,
            'V_col1': V_col1, 'V_beam': V_beam, 'V_col2': V_col2,
            'N_col1': N_col1, 'N_beam': N_beam, 'N_col2': N_col2,
            'key_values': {
                'M1': M1, 'M2': M2, 'M_max_beam': M_max_beam, 'x_max': x_max,
                'V_beam_start': V_beam[0], 'V_beam_end': V_beam[-1],
                'N_col1': N_col1[0], 'N_beam': N_beam[0], 'N_col2': N_col2[0]
            }
        }
