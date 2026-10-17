"""Fake, cassette, template and a disabled real-provider guard."""

from roi_and_build_vs_buy.evalkit.commentary.base import Provider
from roi_and_build_vs_buy.evalkit.commentary.cassette import CassetteProvider
from roi_and_build_vs_buy.evalkit.commentary.fake import FakeProvider
from roi_and_build_vs_buy.evalkit.commentary.real import RealProvider
from roi_and_build_vs_buy.evalkit.commentary.template import TemplateProvider
from roi_and_build_vs_buy.roi.config import Settings


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
