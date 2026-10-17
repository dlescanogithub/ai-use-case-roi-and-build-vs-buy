"""Fake, cassette, template and a disabled real-provider guard."""

from roi_model.config import Settings
from roi_model.evalkit.providers.base import Provider
from roi_model.evalkit.providers.cassette import CassetteProvider
from roi_model.evalkit.providers.fake import FakeProvider
from roi_model.evalkit.providers.real import RealProvider
from roi_model.evalkit.providers.template import TemplateProvider


def build_provider(settings: Settings) -> Provider:
    if settings.provider == "template":
        return TemplateProvider()
    if settings.provider == "fake":
        return FakeProvider()
    if settings.provider == "cassette":
        return CassetteProvider(settings.cassette_path)
    if settings.provider == "real":
        return RealProvider(
            enabled=settings.enable_real_provider,
            api_key=settings.provider_api_key,
        )
    raise ValueError(f"unknown provider {settings.provider}")
