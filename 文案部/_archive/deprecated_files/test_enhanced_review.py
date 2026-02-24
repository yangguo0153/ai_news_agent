"""
测试增强后的审核逻辑
"""

from swarm_with_llm import check_scene_quality, check_emotion_quality

def test_scene_quality():
    """测试场景化程度检查"""
    print("=" * 60)
    print("测试场景化程度检查")
    print("=" * 60)

    # 测试1: 高质量内容
    content1 = """每到春节，心就早早飞回了老家。以前开轿车回家，最怕长途。父母蜷在后排，时间一长就腰酸背痛。如今换了CR-V，父母坐得舒展。后备箱塞满年货，后排空间宽敞，高速上Honda SENSING系统默默护航。"""

    result1 = check_scene_quality(content1)
    print(f"\n测试1（高质量）:")
    print(f"  评分: {result1['score']}/10")
    print(f"  有场景: {result1['has_scene']}")
    print(f"  有细节: {result1['has_detail']}")
    print(f"  反馈: {result1['feedback']}")

    # 测试2: 低质量内容
    content2 = """CR-V是一款很好的车。它有很大的空间，很安全。我很喜欢这辆车。它的性能很好，价格也合理。"""

    result2 = check_scene_quality(content2)
    print(f"\n测试2（低质量）:")
    print(f"  评分: {result2['score']}/10")
    print(f"  有场景: {result2['has_scene']}")
    print(f"  有细节: {result2['has_detail']}")
    print(f"  反馈: {result2['feedback']}")


def test_emotion_quality():
    """测试情感共鸣度检查"""
    print("\n" + "=" * 60)
    print("测试情感共鸣度检查")
    print("=" * 60)

    # 测试1: 高质量内容
    content1 = """那份牵挂比行李还沉。我握着方向盘，手心都是汗。父母坐得舒展，轻声说这车稳当，脸上的笑意，是我路上最美的风景。回家的路，因守护而温暖，因团圆而圆满。"""

    result1 = check_emotion_quality(content1)
    print(f"\n测试1（高质量）:")
    print(f"  评分: {result1['score']}/10")
    print(f"  有情感: {result1['has_emotion']}")
    print(f"  有温暖: {result1['has_warmth']}")
    print(f"  反馈: {result1['feedback']}")

    # 测试2: 低质量内容
    content2 = """CR-V的空间很大，可以装很多东西。后排座椅很舒适，开起来很平稳。这是一辆不错的车。"""

    result2 = check_emotion_quality(content2)
    print(f"\n测试2（低质量）:")
    print(f"  评分: {result2['score']}/10")
    print(f"  有情感: {result2['has_emotion']}")
    print(f"  有温暖: {result2['has_warmth']}")
    print(f"  反馈: {result2['feedback']}")


if __name__ == "__main__":
    test_scene_quality()
    test_emotion_quality()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
