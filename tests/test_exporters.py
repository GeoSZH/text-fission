import pytest
import os
import json
import pandas as pd
import tempfile
from pathlib import Path
from textfission.core.config import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
from textfission.exporters.base import (
    DatasetExporter,
    JSONExporter,
    CSVExporter,
    TXTExporter
)

class TestJSONExporter:
    """测试JSON导出器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(
                format="json",
                encoding="utf-8",
                indent=2
            ),
            custom_config=CustomConfig()
        )
        self.exporter = JSONExporter(self.config)
        self.test_data = [
            {
                "text": "Python is a programming language.",
                "question": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "confidence": 0.95
            },
            {
                "text": "Python was created by Guido van Rossum.",
                "question": "Who created Python?",
                "answer": "Guido van Rossum created Python.",
                "confidence": 0.98
            }
        ]

    def test_exporter_initialization(self):
        """测试导出器初始化"""
        assert self.exporter.config is not None
        assert self.exporter.indent == 2
        assert self.exporter.encoding == "utf-8"

    def test_export_json(self):
        """测试JSON导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name
        
        try:
            # 导出数据
            result_path = self.exporter.export(self.test_data, output_path)
            assert result_path == output_path
            
            # 验证文件存在
            assert os.path.exists(output_path)
            
            # 验证内容
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data == self.test_data
        finally:
            os.unlink(output_path)

    def test_export_json_with_custom_encoding(self):
        """测试自定义编码的JSON导出"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(encoding="utf-8"),
            custom_config=CustomConfig()
        )
        exporter = JSONExporter(config)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name
        
        try:
            result_path = exporter.export(self.test_data, output_path)
            assert os.path.exists(result_path)
        finally:
            os.unlink(output_path)

class TestCSVExporter:
    """测试CSV导出器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(
                format="csv",
                encoding="utf-8"
            ),
            custom_config=CustomConfig()
        )
        self.exporter = CSVExporter(self.config)
        self.test_data = [
            {
                "text": "Python is a programming language.",
                "question": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "confidence": 0.95
            },
            {
                "text": "Python was created by Guido van Rossum.",
                "question": "Who created Python?",
                "answer": "Guido van Rossum created Python.",
                "confidence": 0.98
            }
        ]

    def test_exporter_initialization(self):
        """测试导出器初始化"""
        assert self.exporter.config is not None
        assert self.exporter.encoding == "utf-8"

    def test_export_csv(self):
        """测试CSV导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = f.name
        
        try:
            # 导出数据
            result_path = self.exporter.export(self.test_data, output_path)
            assert result_path == output_path
            
            # 验证文件存在
            assert os.path.exists(output_path)
            
            # 验证内容
            df = pd.read_csv(output_path)
            assert len(df) == len(self.test_data)
            assert list(df.columns) == list(self.test_data[0].keys())
        finally:
            os.unlink(output_path)

    def test_export_csv_with_empty_data(self):
        """测试空数据的CSV导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = f.name
        
        try:
            result_path = self.exporter.export([], output_path)
            assert os.path.exists(result_path)
        finally:
            os.unlink(output_path)

class TestTXTExporter:
    """测试TXT导出器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(
                format="txt",
                encoding="utf-8",
                separator="\n\n"
            ),
            custom_config=CustomConfig()
        )
        self.exporter = TXTExporter(self.config)
        self.test_data = [
            {
                "text": "Python is a programming language.",
                "question": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "confidence": 0.95
            },
            {
                "text": "Python was created by Guido van Rossum.",
                "question": "Who created Python?",
                "answer": "Guido van Rossum created Python.",
                "confidence": 0.98
            }
        ]

    def test_exporter_initialization(self):
        """测试导出器初始化"""
        assert self.exporter.config is not None
        assert self.exporter.encoding == "utf-8"
        assert self.exporter.separator == "\n\n"

    def test_export_txt(self):
        """测试TXT导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            output_path = f.name
        
        try:
            # 导出数据
            result_path = self.exporter.export(self.test_data, output_path)
            assert result_path == output_path
            
            # 验证文件存在
            assert os.path.exists(output_path)
            
            # 验证内容
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "Question: What is Python?" in content
            assert "Answer: Python is a high-level programming language." in content
            assert "Question: Who created Python?" in content
            assert "Answer: Guido van Rossum created Python." in content
        finally:
            os.unlink(output_path)

    def test_export_txt_with_custom_separator(self):
        """测试自定义分隔符的TXT导出"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(separator="---"),
            custom_config=CustomConfig()
        )
        exporter = TXTExporter(config)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            output_path = f.name
        
        try:
            result_path = exporter.export(self.test_data, output_path)
            assert os.path.exists(result_path)
            
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "---" in content
        finally:
            os.unlink(output_path)

class TestDatasetExporter:
    """测试数据集导出器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(
                format="json",
                encoding="utf-8",
                indent=2
            ),
            custom_config=CustomConfig()
        )
        self.exporter = DatasetExporter(self.config)
        self.test_data = [
            {
                "text": "Python is a programming language.",
                "question": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "confidence": 0.95
            }
        ]

    def test_exporter_initialization(self):
        """测试导出器初始化"""
        assert self.exporter.config is not None
        assert "json" in self.exporter.exporters
        assert "csv" in self.exporter.exporters
        assert "txt" in self.exporter.exporters

    def test_export_single_format(self):
        """测试单格式导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name
        
        try:
            # 导出数据
            result_path = self.exporter.export(self.test_data, output_path)
            assert result_path == output_path
            
            # 验证文件存在
            assert os.path.exists(output_path)
        finally:
            os.unlink(output_path)

    def test_export_multiple_formats(self):
        """测试多格式导出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            formats = ["json", "csv", "txt"]
            
            # 导出到多种格式
            results = self.exporter.export_multiple(self.test_data, temp_dir, formats)
            
            # 验证结果
            assert len(results) == len(formats)
            for format, path in results.items():
                assert os.path.exists(path)
                assert path.endswith(f".{format}")

    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        formats = self.exporter.get_supported_formats()
        assert "json" in formats
        assert "csv" in formats
        assert "txt" in formats
        assert len(formats) == 3

    def test_export_with_format_extension(self):
        """测试通过文件扩展名确定格式"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_path = f.name
        
        try:
            # 不指定格式，通过扩展名自动确定
            result_path = self.exporter.export(self.test_data, output_path)
            assert result_path == output_path
            assert os.path.exists(output_path)
        finally:
            os.unlink(output_path)

    def test_export_invalid_format(self):
        """测试无效格式导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".invalid", delete=False) as f:
            output_path = f.name
        
        try:
            # 测试无效格式
            with pytest.raises(Exception):
                self.exporter.export(self.test_data, output_path, "invalid")
        finally:
            os.unlink(output_path)

    def test_export_with_nonexistent_directory(self):
        """测试导出到不存在的目录"""
        nonexistent_dir = "/tmp/nonexistent_dir_for_testing"
        output_path = os.path.join(nonexistent_dir, "test.json")
        
        # 应该自动创建目录
        result_path = self.exporter.export(self.test_data, output_path)
        assert os.path.exists(result_path)
        
        # 清理
        os.unlink(result_path)
        os.rmdir(nonexistent_dir)

class TestExportIntegration:
    """测试导出集成"""
    
    def test_export_workflow(self):
        """测试导出工作流程"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        # 测试所有导出器都能正确初始化
        json_exporter = JSONExporter(config)
        csv_exporter = CSVExporter(config)
        txt_exporter = TXTExporter(config)
        dataset_exporter = DatasetExporter(config)
        
        assert json_exporter is not None
        assert csv_exporter is not None
        assert txt_exporter is not None
        assert dataset_exporter is not None
        
        # 测试数据
        test_data = [
            {
                "text": "Test text",
                "question": "Test question?",
                "answer": "Test answer",
                "confidence": 0.9
            }
        ]
        
        # 测试所有格式的导出
        with tempfile.TemporaryDirectory() as temp_dir:
            # JSON导出
            json_path = os.path.join(temp_dir, "test.json")
            json_result = json_exporter.export(test_data, json_path)
            assert os.path.exists(json_result)
            
            # CSV导出
            csv_path = os.path.join(temp_dir, "test.csv")
            csv_result = csv_exporter.export(test_data, csv_path)
            assert os.path.exists(csv_result)
            
            # TXT导出
            txt_path = os.path.join(temp_dir, "test.txt")
            txt_result = txt_exporter.export(test_data, txt_path)
            assert os.path.exists(txt_result)
            
            # 数据集导出器多格式导出
            results = dataset_exporter.export_multiple(test_data, temp_dir, ["json", "csv", "txt"])
            assert len(results) == 3
            for path in results.values():
                assert os.path.exists(path)

    def test_export_data_integrity(self):
        """测试导出数据完整性"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        # 复杂测试数据
        test_data = [
            {
                "text": "Python is a programming language.",
                "question": "What is Python?",
                "answer": "Python is a high-level programming language.",
                "confidence": 0.95,
                "metadata": {"source": "test", "timestamp": "2023-01-01"}
            },
            {
                "text": "Python was created by Guido van Rossum.",
                "question": "Who created Python?",
                "answer": "Guido van Rossum created Python.",
                "confidence": 0.98,
                "metadata": {"source": "test", "timestamp": "2023-01-01"}
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试JSON导出数据完整性
            json_path = os.path.join(temp_dir, "test.json")
            json_exporter = JSONExporter(config)
            json_exporter.export(test_data, json_path)
            
            with open(json_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            assert loaded_data == test_data
            
            # 测试CSV导出数据完整性
            csv_path = os.path.join(temp_dir, "test.csv")
            csv_exporter = CSVExporter(config)
            csv_exporter.export(test_data, csv_path)
            
            df = pd.read_csv(csv_path)
            assert len(df) == len(test_data)
            assert "text" in df.columns
            assert "question" in df.columns
            assert "answer" in df.columns
            assert "confidence" in df.columns 