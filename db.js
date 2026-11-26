/* ============================================================
   db.js — GameStore 와 Supabase 를 잇는 연결 코드 (모든 html 이 함께 쓴다)
   불러오는 순서: supabase-js(CDN) → db.js → 각 페이지의 스크립트

   넣어도 되는 값은 두 가지뿐이다: Project URL 과 Publishable key.
   Secret key · DB 비밀번호 · 로그인 비밀번호는 절대 넣지 않는다.
   표: shop_profiles(회원) · shop_products(상품) · shop_orders(주문) · shop_order_items(주문 상세)
   ============================================================ */
const SUPABASE_URL = 'https://bistmkyoyfpmrkiukajx.supabase.co';
const SUPABASE_KEY = 'sb_publishable_DRyjP29aR1KdAMg-ogiTEg_HLRnBrr-';

const db = window.supabase ? window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY) : null;

// 연결 확인: 페이지가 열리면 상품 수를 세어 콘솔(F12)에 찍는다
(async () => {
  if (!db){
    console.error('연결 실패: supabase-js 를 불러오지 못했어요 (인터넷 연결이나 CDN 주소를 확인)');
    return;
  }
  const { count, error } = await db.from('shop_products').select('*', { count: 'exact', head: true });
  if (error) console.error('연결 실패:', error.message);
  else console.log(`연결 성공: 상품 ${count}개`);
})();
