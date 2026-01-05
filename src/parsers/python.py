import ast
from pathlib import Path
from typing import List
from src.parsers.base import BaseParser
from src.storage import Symbol


class SymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path) -> None:
        self.symbols: List[Symbol] = []
        self.file_path = str(file_path)
        # stack to trace class context
        # if len > 0 -> inside class
        self.__class_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.symbols.append(
            Symbol(
                symbol_name=node.name,
                symbol_type="class",
                file_path=self.file_path,
                line_number=node.lineno,
                signature="",
                docstring=self.__get_docstring(node),
            )
        )

        self.__class_stack.append(node.name)
        self.generic_visit(node)
        self.__class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        is_method = len(self.__class_stack) > 0
        symbol_type = "method" if is_method else "function"

        self.symbols.append(
            Symbol(
                symbol_name=node.name,
                symbol_type=symbol_type,
                file_path=self.file_path,
                line_number=node.lineno,
                signature=self.__get_signature(node),
                docstring=self.__get_docstring(node),
            )
        )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore

    def __get_docstring(self, node) -> str:
        doc = ast.get_docstring(node)
        return doc.strip() if doc else ""

    def __get_signature(self, node: ast.FunctionDef) -> str:
        args = ast.unparse(node.args)
        returns = ""
        if node.returns:
            returns = f"  -> {ast.unparse(node.returns)}"
        return f"({args}){returns}"


class PythonParser(BaseParser):
    def parse_file(self, file_path: Path) -> List[Symbol]:
        try:
            with open(file_path, "r") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            visitor = SymbolVisitor(file_path)
            visitor.visit(tree)

            return visitor.symbols
        except Exception:
            return []

    @property
    def extensions(self) -> List[str]:
        return [".py"]
