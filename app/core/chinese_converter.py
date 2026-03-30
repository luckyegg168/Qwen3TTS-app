"""Chinese Simplified/Traditional conversion utilities"""

try:
    import opencc

    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False


class ChineseConverter:
    S2T_MODE = "s2t"
    T2S_MODE = "t2s"
    S2T_TW_MODE = "s2tw"
    T2S_TW_MODE = "tw2s"
    S2T_HK_MODE = "s2hk"
    T2S_HK_MODE = "hk2s"

    def __init__(self, mode: str = T2S_MODE):
        self.mode = mode
        self._converter = None
        if HAS_OPENCC:
            self._init_converter()

    def _init_converter(self):
        config_map = {
            self.S2T_MODE: "s2t.json",
            self.T2S_MODE: "t2s.json",
            self.S2T_TW_MODE: "s2tw.json",
            self.T2S_TW_MODE: "tw2s.json",
            self.S2T_HK_MODE: "s2hk.json",
            self.T2S_HK_MODE: "hk2s.json",
        }
        config = config_map.get(self.mode, "t2s.json")
        self._converter = opencc.OpenCC(config)

    def convert(self, text: str) -> str:
        if not text.strip():
            return text

        if HAS_OPENCC and self._converter:
            return self._converter.convert(text)

        return self._fallback_convert(text)

    def _fallback_convert(self, text: str) -> str:
        if self.mode in (self.T2S_MODE, self.S2T_TW_MODE, self.S2T_HK_MODE):
            return self._zh2Hans(text)
        else:
            return self._zh2Hant(text)

    @staticmethod
    def s2t(text: str) -> str:
        return ChineseConverter(ChineseConverter.S2T_MODE).convert(text)

    @staticmethod
    def t2s(text: str) -> str:
        return ChineseConverter(ChineseConverter.T2S_MODE).convert(text)

    @staticmethod
    def s2tw(text: str) -> str:
        return ChineseConverter(ChineseConverter.S2T_TW_MODE).convert(text)

    @staticmethod
    def tw2s(text: str) -> str:
        return ChineseConverter(ChineseConverter.T2S_TW_MODE).convert(text)

    @staticmethod
    def s2hk(text: str) -> str:
        return ChineseConverter(ChineseConverter.S2T_HK_MODE).convert(text)

    @staticmethod
    def hk2s(text: str) -> str:
        return ChineseConverter(ChineseConverter.T2S_HK_MODE).convert(text)

    @staticmethod
    def _zh2Hans(text: str) -> str:
        if not HAS_OPENCC:
            return text
        converter = opencc.OpenCC("t2s.json")
        return converter.convert(text)

    @staticmethod
    def _zh2Hant(text: str) -> str:
        if not HAS_OPENCC:
            return text
        converter = opencc.OpenCC("s2t.json")
        return converter.convert(text)
