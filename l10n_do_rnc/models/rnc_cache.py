import json
import gzip
import os
import logging
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class RNCCache(models.AbstractModel):
    _name = 'rnc.cache'
    _description = 'RNC Cache Manager'
    
    def _get_data_file_path(self):
        """Returns the path to the data file"""
        module_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(module_path, 'data', 'rnc_data.json.gz')

    def search_rnc(self, rnc):
        """Searches for RNC directly in the data file"""
        try:
            file_path = self._get_data_file_path()
            if os.path.exists(file_path):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Search for RNC in the list
                    for item in data:
                        if item.get('rnc') == rnc:
                            return item.get('name', False)
                    
                    return False
            else:
                _logger.warning("Archivo de datos RNC no encontrado en: %s", file_path)
                return False
                
        except Exception as e:
            _logger.error(f"Error buscando RNC {rnc}: {e}")
            return False

    def get_cache_stats(self):
        """Returns statistics of the data file"""
        try:
            file_path = self._get_data_file_path()
            if os.path.exists(file_path):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        'loaded': True,
                        'records': len(data)
                    }
            else:
                return {'loaded': False, 'records': 0}
                
        except Exception as e:
            _logger.error(f"Error obteniendo estadísticas: {e}")
            return {'loaded': False, 'records': 0}

    def clear_cache(self):
        """Method of compatibility - does nothing since there is no cache"""
        _logger.info("No cache to clear - data is read directly from the file")

    def reload_cache(self):
        """Method of compatibility - returns current statistics"""
        return self.get_cache_stats() 