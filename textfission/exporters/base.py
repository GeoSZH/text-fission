from typing import List, Dict, Any, Optional
from ..core.base import BaseExporter
from ..core.exceptions import ExportError
import json
import csv
import pandas as pd
import os
from pathlib import Path

class JSONExporter(BaseExporter):
    """JSON format exporter"""
    
    def __init__(self, config):
        super().__init__(config)
        self.indent = config.export_config.indent or 2
        self.encoding = config.export_config.encoding or "utf-8"

    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export data to JSON file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write data to file
            with open(output_path, "w", encoding=self.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=self.indent)
            
            return output_path
        except Exception as e:
            raise ExportError(f"Error exporting to JSON: {str(e)}")

class CSVExporter(BaseExporter):
    """CSV format exporter"""
    
    def __init__(self, config):
        super().__init__(config)
        self.encoding = config.export_config.encoding or "utf-8"

    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export data to CSV file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Write to CSV
            df.to_csv(output_path, index=False, encoding=self.encoding)
            
            return output_path
        except Exception as e:
            raise ExportError(f"Error exporting to CSV: {str(e)}")

class TXTExporter(BaseExporter):
    """TXT format exporter"""
    
    def __init__(self, config):
        super().__init__(config)
        self.encoding = config.export_config.encoding or "utf-8"
        self.separator = config.export_config.separator or "\n\n"

    def export(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """Export data to TXT file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert data to text
            text = self.separator.join([
                f"Question: {item['question']}\nAnswer: {item['answer']}"
                for item in data
            ])
            
            # Write to file
            with open(output_path, "w", encoding=self.encoding) as f:
                f.write(text)
            
            return output_path
        except Exception as e:
            raise ExportError(f"Error exporting to TXT: {str(e)}")

class DatasetExporter:
    """Main dataset exporter class"""
    
    def __init__(self, config):
        self.config = config
        self.exporters = {
            "json": JSONExporter(config),
            "csv": CSVExporter(config),
            "txt": TXTExporter(config)
        }

    def export(self, data: List[Dict[str, Any]], output_path: str, format: Optional[str] = None) -> str:
        """Export dataset to specified format"""
        try:
            # Determine format from file extension if not specified
            if not format:
                format = Path(output_path).suffix[1:].lower()
            
            # Get exporter
            exporter = self.exporters.get(format)
            if not exporter:
                raise ExportError(f"Unsupported export format: {format}")
            
            # Export data
            return exporter.export(data, output_path)
        except Exception as e:
            raise ExportError(f"Error exporting dataset: {str(e)}")

    def export_multiple(self, data: List[Dict[str, Any]], output_dir: str, formats: List[str]) -> Dict[str, str]:
        """Export dataset to multiple formats"""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Export to each format
            results = {}
            for format in formats:
                output_path = os.path.join(output_dir, f"dataset.{format}")
                results[format] = self.export(data, output_path, format)
            
            return results
        except Exception as e:
            raise ExportError(f"Error exporting dataset to multiple formats: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return list(self.exporters.keys()) 