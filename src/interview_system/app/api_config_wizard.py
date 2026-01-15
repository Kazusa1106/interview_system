#!/usr/bin/env python3
# coding: utf-8
"""API Configuration Wizard - Interactive setup for LLM providers"""

from typing import Optional, Dict

from interview_system.common.logger import get_logger
from interview_system.integrations.api_helpers import initialize_api, get_api_client, get_available_providers

log = get_logger(__name__)


class APIConfigWizard:
    """Interactive API configuration wizard"""

    def __init__(self):
        self.client = get_api_client()
        self.providers = get_available_providers()

    def run(self) -> bool:
        """
        Run interactive configuration wizard

        Returns:
            True if API configured successfully
        """
        print("\n===== 智能追问 API 配置 =====")

        if self._try_use_saved_config():
            return True

        return self._configure_new_api()

    def _try_use_saved_config(self) -> bool:
        """Try to use saved configuration"""
        if not (self.client.current_provider and self.client.api_key):
            return False

        log.info("检测到已保存的API配置", extra={
            "provider": self.client.current_provider.name,
            "model": self.client.model
        })
        print(f"已检测到本地保存的配置：{self.client.current_provider.name}")
        print(f"模型：{self.client.model}")

        use_saved = input("\n是否使用已保存的配置？(Y/n): ").strip().lower()
        if use_saved == 'n':
            return False

        success = self.client.initialize(
            self.client.current_provider.provider_id,
            self.client.api_key,
            self.client.secret_key,
            self.client.model
        )

        if success:
            log.info("API配置验证成功", extra={"provider": self.client.current_provider.name})
            print(f"✅ {self.client.current_provider.name} 智能追问功能已启用")
            return True

        log.warning("已保存的API配置验证失败")
        return False

    def _configure_new_api(self) -> bool:
        """Configure new API from scratch"""
        provider_id = self._select_provider()
        if not provider_id:
            return False

        provider = self.providers[provider_id]
        credentials = self._collect_credentials(provider)
        if not credentials:
            return False

        model = self._select_model(provider)
        return self._validate_and_save(provider_id, credentials, model)

    def _select_provider(self) -> Optional[str]:
        """Select API provider"""
        self._display_providers()

        provider_list = list(self.providers.keys())
        while True:
            choice = input(f"\n请选择 API 提供商 [0-{len(provider_list)}]: ").strip()

            if choice in ('0', ''):
                log.info("用户跳过API配置，使用预设追问")
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(provider_list):
                    return provider_list[idx]
            except ValueError:
                if choice in self.providers:
                    return choice

            print("无效选择，请重新输入")

    def _display_providers(self):
        """Display available providers"""
        print("\n支持的 API 提供商：")
        print("-" * 50)
        for i, (pid, provider) in enumerate(self.providers.items(), 1):
            print(f"  {i}. {provider.name}")
            print(f"     官网：{provider.website}")
        print(f"  0. 跳过配置（使用预设追问）")
        print("-" * 50)

    def _collect_credentials(self, provider) -> Optional[Dict]:
        """Collect API credentials"""
        log.info("用户选择API提供商", extra={"provider": provider.name})
        print(f"\n已选择：{provider.name}")
        print(f"获取 API Key：{provider.website}")

        if provider.provider_id == "deepseek":
            self._show_deepseek_warning()

        print("-" * 50)

        api_key = input(f"请输入 {provider.api_key_name}: ").strip()
        if not api_key:
            log.info("用户未输入API Key，使用预设追问")
            return None

        secret_key = None
        if provider.need_secret_key:
            secret_key = input("请输入 Secret Key: ").strip()
            if not secret_key:
                log.info("用户未输入Secret Key，使用预设追问")
                return None

        return {"api_key": api_key, "secret_key": secret_key}

    def _show_deepseek_warning(self):
        """Show warning for DeepSeek model selection"""
        log.info("显示deepseek模型选择提示")
        print("\n⚠️ 注意：请使用 deepseek-chat 模型")
        print("   不要使用 deepseek-reasoner (R1)，推理模型不适合对话场景")

    def _select_model(self, provider) -> Optional[str]:
        """Select model from provider's available models"""
        if not provider.models or len(provider.models) <= 1:
            return None

        print(f"\n可用模型：")
        for i, m in enumerate(provider.models, 1):
            default_mark = " (默认)" if m == provider.default_model else ""
            print(f"  {i}. {m}{default_mark}")

        model_choice = input(f"选择模型 [直接回车使用默认]: ").strip()
        if not model_choice:
            return None

        try:
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(provider.models):
                return provider.models[model_idx]
        except ValueError:
            pass

        return None

    def _validate_and_save(self, provider_id: str, credentials: Dict, model: Optional[str]) -> bool:
        """Validate API and save configuration"""
        provider = self.providers[provider_id]
        log.info("开始验证API配置", extra={
            "provider": provider_id,
            "model": model or provider.default_model
        })
        print("\n正在验证 API 配置...")

        success = initialize_api(
            provider_id,
            credentials["api_key"],
            credentials.get("secret_key"),
            model
        )

        if success:
            self.client.save_config()
            log.info("API配置验证成功并已保存", extra={
                "provider": provider.name,
                "model": self.client.model
            })
            print(f"✅ {provider.name} 智能追问功能已启用")
            print(f"   模型：{self.client.model}")
            return True

        log.error("API配置验证失败", extra={"provider": provider.name})
        log.info("回退至预设追问模式")
        return False
