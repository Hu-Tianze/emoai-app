export function getMoodKeywords(emotions: Record<string, number>) {
  const positiveEmotions = ['happy', 'content', 'calm'];

  // 1. 将情绪对象转为数组并排序
  const sortedEmotions = Object.entries(emotions)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  // 2. 选取占比最高的两项
  const topTwo = sortedEmotions.slice(0, 2);
  const keywords = topTwo.map(e => e.name);

  // 如果没有足够的情绪数据，直接返回
  if (topTwo.length < 2) {
    return keywords.slice(0, 3);
  }

  // 3. 判断前两项是否为同一类
  const topTwoFirst = topTwo[0];
  const topTwoSecond = topTwo[1];

  if (!topTwoFirst || !topTwoSecond) {
    return keywords.slice(0, 3);
  }

  const isTopTwoSameCategory =
    (positiveEmotions.includes(topTwoFirst.name) && positiveEmotions.includes(topTwoSecond.name)) ||
    (!positiveEmotions.includes(topTwoFirst.name) && !positiveEmotions.includes(topTwoSecond.name));

  if (isTopTwoSameCategory) {
    // 4a. 如果是同一类，则从另一类中选取占比最高的一项
    const topOneCategory = positiveEmotions.includes(topTwoFirst.name) ? 'positive' : 'negative';
    const otherCategoryEmotions = sortedEmotions.filter(e => {
      const isPositive = positiveEmotions.includes(e.name);
      return topOneCategory === 'positive' ? !isPositive : isPositive;
    });
    if (otherCategoryEmotions.length > 0) {
      const otherFirst = otherCategoryEmotions[0];
      if (otherFirst) {
        keywords.push(otherFirst.name);
      }
    }
  } else {
    // 4b. 如果不是同一类，则直接选取占比第三的项
    if (sortedEmotions.length > 2) {
      const thirdItem = sortedEmotions[2];
      if (thirdItem) {
        keywords.push(thirdItem.name);
      }
    }
  }

  // 返回最终的三个关键词
  return keywords.slice(0, 3);
}
