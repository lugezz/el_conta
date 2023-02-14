DEDUCCIONES = {
                'deduccion': {
                    '1': 'Cuotas Médico-Asistenciales',
                    '2': 'Primas de Seguro para el caso de muerte',
                    '3': 'Donaciones',
                    '4': 'Intereses Préstamo Hipotecario',
                    '5': 'Gastos de Sepelio',
                    '7': 'Gastos Médicos y Paramédicos',
                    '8': 'Deducción del Personal Doméstico',
                    '9': 'Aporte a Sociedades de Garantía Recíproca',
                    '10': 'Vehiculos de Corredores y Viajantes de Comercio',
                    '11': 'Gastos de Representación e Intereses de Corredores y Viajantes de Comercio',
                    '21': 'Gastos de Adquisición de Indumentaria y Equipamiento uso Lugar de Trabajo',
                    '22': 'Alquiler de Inmuebles destinados a casa habitación',
                    '23': 'Primas de Ahorro correspondientes a Seguros Mixtos',
                    '24': 'Aportes correspondientes a Planes de Seguro de Retiro Privados',
                    '25': 'Adquisición de Cuotapartes de Fondos Comunes de Inversión con fines de retiro',
                    '32': 'Herramientas educativas - Servicios con fines educativos',
                    '99': 'Otras Deducciones',
                },
                'cargaFamilia': {
                    '1': 'Cónyuge',
                    '3': 'Hijo/a Menor de 18 Años',
                    '30': 'Hijastro/a Menor de 18 Años',
                    '31': 'Hijo/a Incapacitado para el Trabajo',
                    '32': 'Hijastro/a Incapcacitado para el Trabajo',
                    '51': 'Union convivencial',
                },
                'retPerPago': {
                    '6': 'Impuestos sobre Créditos y Débitos en cuenta Bancaria',
                    '12': 'Retenciones y Percepciones Aduaneras',
                    '13': 'Pago a Cuenta - Compras en el Exterior',
                    '14': 'Impuesto sobre los Movimientos de Fondos Propios o de Terceros',
                    '15': 'Pago a Cuenta - Compra de Paquetes Turísticos',
                    '16': 'Pago a Cuenta - Compra de Pasajes',
                    '17': 'Pago a Cuenta - Compra de Moneda Extranjera para Turismo / Transf. al Exterior',
                    '18': 'Pago a Cuenta - Adquisición de moneda extranjera para tenencia de billetes extranjeros',
                    '19': 'Pago a Cuenta - Compra de Paquetes Turísticos en efectivo',
                    '20': 'Pago a Cuenta - Compra de Pasajes en efectivo',
                    '27': 'Pago a Cuenta - RG 4815 - Ley 27541 - Art. 35 inc. a)',
                    '28': 'Pago a Cuenta - RG 4815 - Ley 27541 - Art. 35 inc. b)',
                    '29': 'Pago a Cuenta - RG 4815 - Ley 27541 - Art. 35 inc. c)',
                    '30': 'Pago a Cuenta - RG 4815 - Ley 27541 - Art. 35 inc. e)',
                    '31': 'Pago a Cuenta - RG 4815 - Ley 27541 - Art. 35 inc. e)',
                },
            }


def get_deduccion(tipo, indice):
    resp = ''
    if DEDUCCIONES.get(tipo):
        resp = DEDUCCIONES[tipo].get(indice)

    if tipo == "GANLIQOTROSEMPENT":
        resp = f"{tipo} - {indice}"

    return resp
