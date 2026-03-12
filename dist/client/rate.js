/**
 * 星評価UIのクライアントサイドスクリプト
 *
 * 星ボタンのクリックを検知し、POST /api/rate に送信する。
 * レスポンス成功後にUIの星をアクティブ状態に更新する。
 */

document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".star");
  if (!btn) return;

  const container = btn.closest(".star-rating");
  if (!container) return;

  const rating = Number(btn.dataset.value);
  const paperId = container.dataset.paperId;
  const title = container.dataset.title;
  const abstract = container.dataset.abstract;

  // 楽観的UI更新
  updateStars(container, rating);

  try {
    const res = await fetch("/api/rate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paper_id: paperId, title, abstract, rating }),
    });

    if (!res.ok) {
      console.error("[rate] API error:", res.status);
      // 失敗時は元の評価に戻す
      const prev = Number(container.dataset.rating);
      updateStars(container, prev);
    } else {
      container.dataset.rating = String(rating);
    }
  } catch (err) {
    console.error("[rate] fetch error:", err);
  }
});

function updateStars(container, rating) {
  container.querySelectorAll(".star").forEach((star) => {
    const val = Number(star.dataset.value);
    star.classList.toggle("active", val <= rating);
  });
}
