from typing import Literal



class DataStorage:
    """
    A simple class to store data objects utilizing dictionary data structure.
    """
    def __init__(self):
        self.data = {}


    def is_empty(self):
        return len(self.data) == 0


    def generate_placeholders(
        self,
        keys: list[str] | tuple[str] | set[str],
        default_value=None
    ):
        self.add(
            {key: default_value for key in keys}
        )


    def add(self, data_dict: dict = {}, force_update: bool = False, **kwargs):
        # combine kwargs and data_dict into a single dictionary
        combined_data = {**kwargs}
        if data_dict:
            combined_data.update(data_dict)

        for key, value in combined_data.items():
            if key not in self.data:
                self.data[key] = value
            else:
                if force_update:
                    self.update(**{key: value})
                else:
                    print(f"The item key '{key}' already exists in the data storage.\nUse 'update()' method to update the value.\n")


    def remove(self, key):
        self.data.pop(key, None)


    def update(self, data_dict: dict = {}, force_add: bool = False, **kwargs):
        # combine kwargs and update_dict into a single dictionary
        combined_data = {**kwargs}
        if data_dict:
            combined_data.update(data_dict)

        for key, value in combined_data.items():
            if key in self.data:
                self.data[key] = value
            else:
                if force_add:
                    self.add(**{key: value})
                else:
                    print(f"The item key '{key}' not found in the data storage.\nUse 'add()' method to add a new item.\n")


    def retrieve(self, key):
        query_result = self._find_value_by_key(key)
        if query_result is not None:
            return query_result
        else:
            raise ValueError(f"Key '{key}' not found in the storage.")


    def get(self, key):
        return self.data.get(key, None)


    def get_all(self):
        return self.data


    def get_keys(self):
        return self.data.keys()


    def key_exists(self, key):
        return key in self.data.keys()


    def pair_exists(self, key, value):
        for k, v in self.data.items():
            if k == key and v == value:
                return True
        return False


    @staticmethod
    def find_counterpart_in_single_dictionary(
            dict_obj: dict,
            search_among: Literal["keys", "values"],
            looking_for,
            only_first: bool=False,
            former_trajectory: str="") -> list[dict]:

        results = []
        if len(former_trajectory) == 0:
            former_trajectory = "Root -> "
        for k, v in dict_obj.items():
            result_dict = {
                "key": k,
                "value": v,
                "trajectory": former_trajectory + f"[{k}]"
            }
            if search_among == "keys":
                if k == looking_for:
                    results.append(result_dict)
                    break # no need to continue since keys are unique
            else:
                if v == looking_for:
                    results.append(result_dict)
                    if only_first:
                        break
        return results


    @staticmethod
    def find_counterpart(
            dict_obj: dict,
            search_among: Literal["keys", "values"],
            looking_for,
            only_first: bool = False,
            former_trajectory: str = ""
        ) -> list[dict]:

        results = []
        if len(former_trajectory) == 0:
            former_trajectory = "Root -> "
        for k, v in dict_obj.items():
            trajectory = former_trajectory + f"[{k}]"
            result_dict = {
                "key": k,
                "value": v,
                "trajectory": trajectory
            }
            if search_among == "keys" and k == looking_for:
                results.append(result_dict)
                if only_first:
                    return results
            elif search_among == "values" and v == looking_for:
                results.append(result_dict)
                if only_first:
                    return results

            if isinstance(v, dict):
                nested_results = DataStorage.find_counterpart(v, search_among, looking_for, only_first, trajectory)
                results.extend(nested_results)
                if only_first and nested_results:
                    return results

        return results


    def _find_value_by_key(self, key):
        result = self.find_counterpart(
            dict_obj=self.data,
            search_among="keys",
            looking_for=key,
            only_first=True
        )
        if len(result) > 0:
            return result[0]["value"]
        return None


    def clear(self):
        self.data.clear()


    def __str__(self):
        return str(self.data)


    def __repr__(self):
        parts = [f"'{key}': {{\n\t\t'Type': {type(value)},\n\t\t'Value': {value}\n\t}}" for key, value in self.data.items()]
        return "{\n\t" + ",\n\t".join(parts) + "\n}"
