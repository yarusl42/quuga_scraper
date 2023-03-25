from typing import Dict


class SuccessCriteria:
    def __init__(
            self,
            category_criteria: Dict[str, str] = None,
            node_criteria: Dict[str, str] = None,
            product_criteria: Dict[str, str] = None
    ):
        self.node_criteria = node_criteria
        self.category_criteria = category_criteria
        self.product_criteria = product_criteria

    @staticmethod
    def get_suc_criteria(field: Dict[str, str]) -> str:
        return field.get("success", "")

    def get_node_criteria(self) -> str:
        return self.get_suc_criteria(self.node_criteria)

    def get_category_suc(self) -> str:
        return self.get_suc_criteria(self.category_criteria)

    def get_product_suc(self) -> str:
        return self.get_suc_criteria(self.product_criteria)
