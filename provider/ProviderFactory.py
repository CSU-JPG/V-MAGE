import configparser
import importlib

class ProviderFactory:
    @staticmethod
    def getProvider(llm_provider_config_path, generation_config_path):
        lmm_config = configparser.ConfigParser()
        lmm_config.read(llm_provider_config_path)
        
        provider_name = lmm_config.get('lmm', 'model_name')
        module_path = f"provider.{provider_name}Provider"
        
        try:
            module = importlib.import_module(module_path)
            provider_class = getattr(module, f"{provider_name}Provider")
        except Exception as e:
            provider_class = None
            
        if provider_class is not None:
            # 返回类实例
            return provider_class(llm_provider_config_path, generation_config_path)

        return None