# Módulo l10n_do_rnc - Consulta RNC Offline

Este módulo proporciona funcionalidad para consultar RNCs de forma offline cuando el servicio de DGII no esté disponible.

## Características

- ✅ Consulta RNC online (servicio DGII)
- ✅ Fallback offline automático
- ✅ Cache en memoria para rendimiento óptimo
- ✅ Base de datos comprimida (~5-10MB)
- ✅ Zero-touch deployment

## Estructura del Módulo

```
l10n_do_rnc/
├── data/                    # Datos RNC comprimidos
│   ├── rnc_data.json.gz    # Base de datos RNC
│   └── README.md           # Documentación de datos
├── models/
│   ├── res_partner.py      # Lógica principal (existente)
│   ├── rnc_cache.py        # Cache offline (nuevo)
│   └── __init__.py
├── tools/                   # Herramientas de mantenimiento
│   ├── convert_rnc_data.py # Conversor TXT → JSON
│   ├── update_rnc_data.sh  # Script Linux/Mac
│   ├── update_rnc_data.bat # Script Windows
│   └── __init__.py
├── views/                   # Vistas existentes
├── static/                  # Archivos estáticos
├── i18n/                    # Traducciones
├── __manifest__.py         # Configuración del módulo
└── README.md               # Este archivo
```

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install python-stdnum
   ```

2. **Actualizar módulo:**
   ```bash
   # En Odoo
   -u l10n_do_rnc
   ```

3. **Verificar instalación:**
   ```python
   # En consola Odoo
   stats = self.env['rnc.cache'].get_cache_stats()
   print(f"Cache cargado: {stats['loaded']}")
   print(f"Registros: {stats['records']}")
   ```

## Uso

### Consulta Automática

El módulo funciona automáticamente. Cuando busques un RNC:

1. **Primer intento:** Servicio online de DGII
2. **Fallback:** Base de datos offline (si online falla)
3. **Resultado:** Nombre de la empresa o False

### Verificar Cache

```python
# Obtener estadísticas del cache
stats = self.env['rnc.cache'].get_cache_stats()

# Buscar RNC específico
name = self.env['rnc.cache'].search_rnc('40225809322')

# Recargar cache
stats = self.env['rnc.cache'].reload_cache()
```

## Mantenimiento

### Actualizar Datos RNC

#### Opción 1: Script Automático (Recomendado)

**Linux/Mac:**
```bash
cd src/l10n-dominicana/l10n_do_rnc
./tools/update_rnc_data.sh
```

**Windows:**
```cmd
cd src\l10n-dominicana\l10n_do_rnc
tools\update_rnc_data.bat
```

#### Opción 2: Manual

1. **Descargar archivo TXT:**
   ```bash
   wget https://dgii.gov.do/descargas/rnc/DGII_RNC.TXT
   ```

2. **Convertir a JSON:**
   ```bash
   python3 tools/convert_rnc_data.py DGII_RNC.TXT data/
   ```

3. **Commit y push:**
   ```bash
   git add data/rnc_data.json.gz
   git commit -m "Update RNC data"
   git push
   ```

4. **Actualizar en clientes:**
   ```bash
   # En cada cliente
   -u l10n_do_rnc
   ```

### Programar Actualización Automática

**Linux/Mac (crontab):**
```bash
# Actualizar cada mes
0 2 1 * * /path/to/l10n_do_rnc/tools/update_rnc_data.sh
```

**Windows (Task Scheduler):**
```cmd
# Crear tarea programada para ejecutar update_rnc_data.bat
```

## Rendimiento

- **Primera consulta:** ~100ms (carga cache)
- **Consultas siguientes:** ~1ms (memoria)
- **Memoria utilizada:** ~50-100MB por proceso
- **Tamaño archivo:** ~5-10MB comprimido

## Troubleshooting

### Cache no se carga

```python
# Verificar archivo de datos
import os
file_path = self.env['rnc.cache']._get_data_file_path()
print(f"Archivo existe: {os.path.exists(file_path)}")

# Recargar cache
self.env['rnc.cache'].reload_cache()
```

### Error de conversión

```bash
# Verificar formato del archivo TXT
head -5 DGII_RNC.TXT

# Ejecutar conversión con debug
python3 tools/convert_rnc_data.py DGII_RNC.TXT data/ --verbose
```

### Logs de Odoo

```bash
# Ver logs del módulo
tail -f /var/log/odoo/odoo.log | grep rnc
```

## Desarrollo

### Agregar Fallback a res_partner.py

```python
def get_name_from_dgii(self, vat):
    # ... código existente ...
    
    # Fallback offline (solo para RNCs de 9 dígitos)
    if len(vat) == 9:
        offline_name = self.env['rnc.cache'].search_rnc(vat)
        if offline_name:
            return offline_name
    
    return False
```

### Personalizar Cache

```python
# Modificar comportamiento del cache
class RNCCache(models.AbstractModel):
    _name = 'rnc.cache'
    
    def search_rnc(self, rnc):
        # Lógica personalizada aquí
        pass
```

## Soporte

Para soporte técnico o reportar problemas:

- **Email:** soporte@guavana.com
- **Documentación:** [Wiki del módulo]
- **Issues:** [Repositorio GitHub]

## Licencia

LGPL-3 - Ver archivo LICENSE para más detalles. 