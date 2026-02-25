import re
from typing import Dict, List, Tuple


class SceneRetriever:
    """Lightweight local scene retriever backed by markdown scene library."""

    _SCENE_MARKERS: List[Tuple[str, str]] = [
        ("春节返乡", "## 一、春节返乡场景"),
        ("周末出游", "## 二、周末出游场景"),
        ("日常通勤", "## 三、日常通勤场景"),
        ("亲子游玩", "## 四、亲子游玩场景"),
        ("孝敬父母", "## 五、孝敬父母场景"),
    ]

    _DEFAULT_KEYWORDS: Dict[str, List[str]] = {
        "春节返乡": ["春节", "过年", "返乡", "回家", "团圆", "年货", "春运", "归途"],
        "周末出游": ["周末", "出游", "露营", "郊游", "自驾", "旅行", "风景"],
        "日常通勤": ["通勤", "上班", "下班", "早高峰", "堵车", "代步", "油耗"],
        "亲子游玩": ["亲子", "孩子", "宝宝", "后排", "玩具", "游玩", "陪伴"],
        "孝敬父母": ["父母", "长辈", "老人", "孝敬", "接送", "舒适", "责任"],
    }

    def __init__(
        self,
        scene_library_path: str,
        top_k: int = 3,
        min_score: float = 0.15,
        default_scene: str = "春节返乡",
    ):
        self.scene_library_path = scene_library_path
        self.top_k = max(1, int(top_k))
        self.min_score = float(min_score)
        self.default_scene = default_scene
        self._scene_sections = self._load_scene_sections()

    def _load_scene_sections(self) -> Dict[str, str]:
        try:
            with open(self.scene_library_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return {}

        sections: Dict[str, str] = {}
        for idx, (scene_name, marker) in enumerate(self._SCENE_MARKERS):
            start = content.find(marker)
            if start == -1:
                continue
            end = len(content)
            for next_name, next_marker in self._SCENE_MARKERS[idx + 1 :]:
                pos = content.find(next_marker, start + 1)
                if pos != -1:
                    end = min(end, pos)
            sections[scene_name] = content[start:end]
        return sections

    def _extract_terms(self, text: str) -> List[str]:
        tokens = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", text or "")
        deduped = []
        seen = set()
        for token in tokens:
            norm = token.strip().lower()
            if len(norm) < 2:
                continue
            if norm not in seen:
                seen.add(norm)
                deduped.append(token.strip())
        return deduped

    def _scene_term_set(self, scene_name: str, section_text: str) -> List[str]:
        terms = list(self._DEFAULT_KEYWORDS.get(scene_name, []))
        for term in self._extract_terms(section_text):
            if len(term) <= 6:
                terms.append(term)
        deduped = []
        seen = set()
        for term in terms:
            if term not in seen:
                seen.add(term)
                deduped.append(term)
        return deduped

    def _fallback(self, reason: str, query: str = "") -> Dict:
        evidence = [reason]
        if query:
            evidence.append(f"query={query}")
        return {
            "scene_type": self.default_scene,
            "keywords": [],
            "evidence": evidence,
            "score": 0.0,
            "fallback_used": True,
        }

    def retrieve(self, scene_text: str) -> Dict:
        query = (scene_text or "").strip()
        if not query:
            return self._fallback("empty_input")

        if not self._scene_sections:
            return self._fallback("library_unavailable", query)

        query_terms = self._extract_terms(query)
        if not query_terms:
            return self._fallback("query_unusable", query)

        ranking = []
        for scene_name, section_text in self._scene_sections.items():
            scene_terms = self._scene_term_set(scene_name, section_text)
            matched = []
            for q in query_terms:
                for st in scene_terms:
                    if q in st or st in q:
                        matched.append(st)
                        break
            scene_name_hit = 1 if scene_name in query else 0
            score = (len(matched) + scene_name_hit) / (len(query_terms) + 1)
            ranking.append(
                {
                    "scene_type": scene_name,
                    "score": round(score, 4),
                    "matched": matched,
                }
            )

        ranking.sort(key=lambda item: item["score"], reverse=True)
        best = ranking[0]
        top_candidates = ranking[: self.top_k]
        evidence = [f"{item['scene_type']}:{item['score']:.4f}" for item in top_candidates]

        if best["score"] < self.min_score:
            return {
                "scene_type": self.default_scene,
                "keywords": best["matched"][: self.top_k],
                "evidence": evidence + ["below_threshold"],
                "score": float(best["score"]),
                "fallback_used": True,
            }

        return {
            "scene_type": best["scene_type"],
            "keywords": best["matched"][: self.top_k],
            "evidence": evidence,
            "score": float(best["score"]),
            "fallback_used": False,
        }
