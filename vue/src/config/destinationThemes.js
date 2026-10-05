// 封面占位主题（§7.9.8）：CSS 分层渐变 + 几何风景；按目的地名称哈希取模，不用随机数
// 渐变 A→B→C 统一 linear-gradient(160deg, A, B 55%, C)；将来换真实照片只改本文件
export const DESTINATION_THEMES = [
  {
    key: 'sea',
    keywords: ['海岛', '海滨', '海滩', '海边', '岛', '三亚', '厦门', '青岛', '北海', '普吉'],
    gradient: 'linear-gradient(160deg, #33B1A8, #8ED9C8 55%, #F5EFE6)',
  },
  {
    key: 'town',
    keywords: ['古城', '古镇', '人文', '历史', '西安', '洛阳', '乌镇', '苏州', '杭州', '平遥'],
    gradient: 'linear-gradient(160deg, #8C5A3C, #C99A6E 55%, #EBD6BC)',
  },
  {
    key: 'mtn',
    keywords: ['山地', '自然', '徒步', '森林', '大理', '苍山', '峨眉', '黄山', '张家界', '丽江'],
    gradient: 'linear-gradient(160deg, #5A6E4A, #9CB387 55%, #E4EDD9)',
  },
  {
    key: 'city',
    keywords: ['都市', '城市', '购物', '上海', '北京', '成都', '广州', '深圳', '重庆', '香港'],
    gradient: 'linear-gradient(160deg, #3B4A6B, #7C8AA6 55%, #DDE3ED)',
  },
  {
    key: 'snow',
    keywords: ['雪原', '高寒', '滑雪', '哈尔滨', '长白山', '瑞士', '冰岛', '北海道', '雪'],
    gradient: 'linear-gradient(160deg, #7FA8C9, #C9DCEA 55%, #F4F8FB)',
  },
]

export function destinationTheme(name) {
  const n = name || ''
  for (const t of DESTINATION_THEMES) {
    if (t.keywords.some((k) => n.includes(k))) return t
  }
  // 匹配不到 → 按名称简单哈希取模，同一目的地每次刷新颜色一致（§7.9.8，不用随机数）
  let hash = 0
  for (let i = 0; i < n.length; i++) hash = (hash * 31 + n.charCodeAt(i)) >>> 0
  return DESTINATION_THEMES[hash % DESTINATION_THEMES.length]
}
