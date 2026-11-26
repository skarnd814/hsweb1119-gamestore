-- ============================================================
-- GameStore DB 만들기 (Supabase · 접두어 shop_)
-- 한신대학교 웹프로그래밍(AS006-E) · 13주차 쇼핑몰 & supabase 연결
-- 수업 원본 shop_supabase.sql 을 GameStore 에 맞게 고친 파일
-- ============================================================
--
-- [원본에서 바꾼 곳 — 표시: ★GameStore]
--   1) 등급: WELCOME·SILVER·GOLD·VIP (4단계) → BRONZE·SILVER·GOLD·DIAMOND·LEGEND (5단계)
--      사이트 화면의 브론즈·실버·골드·다이아·레전드 와 같다. 가입하면 BRONZE.
--   2) 가입 포인트: 3,000 → 1,000 (사이트의 「가입 축하 1,000P」)
--   3) 상품 표에 열 3개 추가: name_ko(한글 이름) · developer(개발사) · sale(할인율 %)
--      image_url 에는 사이트의 표지 그림 경로(img/cover-*.png)를 넣는다.
--   4) 예시 상품 6개 → 사이트의 스팀 게임 8개 (가격·할인율·표지 경로 그대로)
--      게임은 내려받는 상품이라 재고(stock)는 넉넉히 9999 로 둔다.
--   보안 규칙(RLS) · 함수 · 주문 표는 원본 그대로다.
--
-- [이 파일을 쓰는 순서]
--   1) 이 파일을 메모장(또는 VS Code)으로 연다
--   2) Ctrl + A (전체 선택) → Ctrl + C (복사)
--   3) Supabase 왼쪽 메뉴 SQL Editor → 위쪽 「+ New」 로 빈 창을 연다
--   4) Ctrl + V (붙여 넣기) → 오른쪽 위 초록 「Run」 (Ctrl + Enter)
--      · 「지우는 명령이 들어 있다」 는 경고 창이 뜨면 내용을 읽고 실행을 누른다
--        (이미 있는 규칙을 지우고 다시 만드는 줄이 있어서 뜨는 경고다 — 데이터는 지우지 않는다)
--   5) 아래 Results 에 Success 가 나오면 끝
--
-- [확인하는 법]
--   왼쪽 메뉴 Table Editor 에 shop_ 으로 시작하는 표 4개가 보인다
--   shop_products 를 누르면 게임 8개가 들어 있다
--
-- [알아 둘 것]
--   · 두 번 실행해도 안전하다 (이미 있으면 건너뛴다)
--   · 줄 앞의 「--」 는 주석이다. 설명일 뿐 실행되지 않는다
--   · 만드는 것은 모두 이름이 shop_ 으로 시작한다 (접두어)
--       shop_profiles     회원 (이름 · 연락처 · 등급 · 포인트 · 역할)
--       shop_products     상품 (이름 · 분류 · 가격 · 할인율 · 재고 · 표지)
--       shop_orders       주문 (누가 · 얼마 · 상태 · 언제)
--       shop_order_items  주문 상세 (주문 한 건에 담긴 상품들)
-- ============================================================

-- 0. 실행 위치 확인 — 「내」 Supabase 프로젝트에서만 실행합니다.
--    다른 사이트가 함께 쓰는 DB(공용 회원 표가 있는 곳)에서는 스스로 멈춥니다.
DO $guard$
BEGIN
  IF to_regclass('public.www_profiles') IS NOT NULL
     OR to_regclass('public.user_profiles') IS NOT NULL THEN
    RAISE EXCEPTION '이 SQL 은 본인이 새로 만든 Supabase 프로젝트에서만 실행하세요. (여기는 다른 사이트가 쓰는 DB 입니다)';
  END IF;
END
$guard$;

-- 1. 회원 표 — 로그인 계정(auth.users) 한 명당 한 줄
--    PRIMARY KEY  : 회원을 하나로 짚는 열
--    REFERENCES   : auth.users 의 id 를 가리키는 외래키 — 계정이 지워지면 이 줄도 지워진다
--    DEFAULT      : 값을 안 넣으면 들어가는 기본값 (가입하면 BRONZE 등급 · 1,000 포인트 · 회원)
--    CHECK        : 정해 둔 값만 받는다 (없는 등급, 음수 포인트를 DB 가 거절한다)
CREATE TABLE IF NOT EXISTS public.shop_profiles (
  id         uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email      text,
  name       text,
  phone      text,
  -- ★GameStore: 5단계 등급 (브론즈 1% · 실버 3% · 골드 5% · 다이아 8% · 레전드 10% 적립)
  grade      text NOT NULL DEFAULT 'BRONZE'
             CONSTRAINT shop_profiles_grade_check
             CHECK (grade IN ('BRONZE', 'SILVER', 'GOLD', 'DIAMOND', 'LEGEND')),
  -- ★GameStore: 가입 축하 1,000P
  points     integer NOT NULL DEFAULT 1000
             CONSTRAINT shop_profiles_points_check CHECK (points >= 0),
  role       text NOT NULL DEFAULT 'member'
             CONSTRAINT shop_profiles_role_check CHECK (role IN ('member', 'admin')),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 2. 상품 표
--    id 는 1, 2, 3 … 으로 자동으로 매겨진다 (GENERATED ALWAYS AS IDENTITY)
--    is_active 가 false 인 상품은 방문자에게 보이지 않는다 (판매 중지에 쓴다)
CREATE TABLE IF NOT EXISTS public.shop_products (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name       text NOT NULL,
  name_ko    text,                                             -- ★GameStore: 한글 이름
  developer  text,                                             -- ★GameStore: 개발사
  category   text NOT NULL,
  price      integer NOT NULL CONSTRAINT shop_products_price_check CHECK (price >= 0),
  sale       integer NOT NULL DEFAULT 0                        -- ★GameStore: 할인율(%)
             CONSTRAINT shop_products_sale_check CHECK (sale BETWEEN 0 AND 90),
  stock      integer NOT NULL DEFAULT 0 CONSTRAINT shop_products_stock_check CHECK (stock >= 0),
  image_url  text,
  is_active  boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- 3. 주문 표 · 주문 상세 표
--    주문 한 건에 상품이 여러 개 담기므로 표를 둘로 나눈다 (1 : N 관계)
--    user_id 의 DEFAULT auth.uid() : 지금 로그인한 사람의 id 가 자동으로 들어간다
--    주문 상세의 기본키는 (order_id, product_id) 두 열을 묶은 복합키다
CREATE TABLE IF NOT EXISTS public.shop_orders (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id    uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
  total      integer NOT NULL CONSTRAINT shop_orders_total_check CHECK (total >= 0),
  status     text NOT NULL DEFAULT '결제완료'
             CONSTRAINT shop_orders_status_check CHECK (status IN ('결제완료', '배송중', '배송완료', '취소')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.shop_order_items (
  order_id   bigint  NOT NULL REFERENCES public.shop_orders(id) ON DELETE CASCADE,
  product_id bigint  NOT NULL REFERENCES public.shop_products(id),
  qty        integer NOT NULL CONSTRAINT shop_order_items_qty_check CHECK (qty > 0),
  unit_price integer NOT NULL CONSTRAINT shop_order_items_price_check CHECK (unit_price >= 0),
  PRIMARY KEY (order_id, product_id)
);

-- 4. 관리자인지 묻는 함수 — 아래 보안 규칙에서 씁니다
CREATE OR REPLACE FUNCTION public.shop_is_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $fn$
  SELECT EXISTS (
    SELECT 1 FROM public.shop_profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
$fn$;

-- 5. 가입하면 회원 표에 한 줄이 자동으로 생기게 합니다
--    (가입 화면에서 보낸 이름 · 연락처를 함께 저장. 등급 · 포인트는 위의 기본값이 들어간다)
CREATE OR REPLACE FUNCTION public.shop_handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $fn$
BEGIN
  BEGIN
    INSERT INTO public.shop_profiles (id, email, name, phone)
    VALUES (NEW.id, NEW.email,
            NEW.raw_user_meta_data ->> 'name',
            NEW.raw_user_meta_data ->> 'phone')
    ON CONFLICT (id) DO NOTHING;
  EXCEPTION WHEN OTHERS THEN
    -- 회원 표에 못 넣어도 가입 자체는 막지 않습니다
    RAISE WARNING 'shop_profiles 자동 생성 실패: %', SQLERRM;
  END;
  RETURN NEW;
END;
$fn$;

DROP TRIGGER IF EXISTS shop_on_auth_user_created ON auth.users;
CREATE TRIGGER shop_on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.shop_handle_new_user();

-- 이 SQL 을 실행하기 전에 이미 가입한 계정이 있으면 회원 표에 채워 넣습니다
INSERT INTO public.shop_profiles (id, email, name, phone)
SELECT u.id, u.email, u.raw_user_meta_data ->> 'name', u.raw_user_meta_data ->> 'phone'
FROM auth.users u
ON CONFLICT (id) DO NOTHING;

-- 6. 관리자가 회원의 등급 · 포인트 · 역할을 바꾸는 함수
--    (회원 관리 페이지가 이 함수를 부릅니다. 관리자가 아니면 거절.
--     없는 등급을 보내면 1번 표의 CHECK 규칙이 거절한다)
CREATE OR REPLACE FUNCTION public.shop_admin_update_member(
  p_user_id uuid, p_grade text, p_points integer, p_role text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $fn$
BEGIN
  IF NOT public.shop_is_admin() THEN
    RAISE EXCEPTION '관리자만 할 수 있습니다' USING ERRCODE = '42501';
  END IF;
  UPDATE public.shop_profiles
     SET grade = p_grade, points = p_points, role = p_role
   WHERE id = p_user_id;
END;
$fn$;

-- 7. 함수 권한 — 로그인하지 않은 방문자는 관리 함수를 부를 수 없게
REVOKE EXECUTE ON FUNCTION public.shop_handle_new_user() FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.shop_admin_update_member(uuid, text, integer, text) FROM PUBLIC, anon;
GRANT  EXECUTE ON FUNCTION public.shop_admin_update_member(uuid, text, integer, text) TO authenticated;
GRANT  EXECUTE ON FUNCTION public.shop_is_admin() TO anon, authenticated;

-- 8. 보안 규칙(RLS) — 「누가 어느 줄을 볼 수 있는가」
--      anon          = 로그인하지 않은 방문자
--      authenticated = 로그인한 회원
--    GRANT  : 표에 어떤 일(SELECT · INSERT · UPDATE · DELETE)을 할 수 있는지
--    POLICY : 그 가운데 「어느 줄」 까지인지
ALTER TABLE public.shop_profiles    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shop_products    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shop_orders      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shop_order_items ENABLE ROW LEVEL SECURITY;

-- 표 권한: 방문자(anon)는 상품만 읽고, 회원(authenticated)은 필요한 것만
REVOKE ALL ON public.shop_profiles, public.shop_products, public.shop_orders, public.shop_order_items FROM anon, authenticated;
GRANT SELECT ON public.shop_products TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.shop_products TO authenticated;
GRANT SELECT ON public.shop_profiles TO authenticated;
GRANT UPDATE (name, phone) ON public.shop_profiles TO authenticated;   -- 등급 · 포인트 · 역할은 본인이 못 바꿉니다
GRANT SELECT, INSERT ON public.shop_orders, public.shop_order_items TO authenticated;
GRANT UPDATE (status) ON public.shop_orders TO authenticated;

-- 회원: 내 정보만 보고 고친다 / 관리자: 모두 본다
DROP POLICY IF EXISTS shop_profiles_select ON public.shop_profiles;
CREATE POLICY shop_profiles_select ON public.shop_profiles
  FOR SELECT TO authenticated
  USING (id = auth.uid() OR public.shop_is_admin());

DROP POLICY IF EXISTS shop_profiles_update_own ON public.shop_profiles;
CREATE POLICY shop_profiles_update_own ON public.shop_profiles
  FOR UPDATE TO authenticated
  USING (id = auth.uid()) WITH CHECK (id = auth.uid());

-- 상품: 누구나 판매 중인 상품을 본다 / 관리자만 넣고 고치고 지운다
DROP POLICY IF EXISTS shop_products_select ON public.shop_products;
CREATE POLICY shop_products_select ON public.shop_products
  FOR SELECT TO anon, authenticated
  USING (is_active OR public.shop_is_admin());

DROP POLICY IF EXISTS shop_products_admin_insert ON public.shop_products;
CREATE POLICY shop_products_admin_insert ON public.shop_products
  FOR INSERT TO authenticated WITH CHECK (public.shop_is_admin());

DROP POLICY IF EXISTS shop_products_admin_update ON public.shop_products;
CREATE POLICY shop_products_admin_update ON public.shop_products
  FOR UPDATE TO authenticated USING (public.shop_is_admin()) WITH CHECK (public.shop_is_admin());

DROP POLICY IF EXISTS shop_products_admin_delete ON public.shop_products;
CREATE POLICY shop_products_admin_delete ON public.shop_products
  FOR DELETE TO authenticated USING (public.shop_is_admin());

-- 주문: 내 주문만 넣고 본다 / 관리자는 모두 보고 상태를 바꾼다
DROP POLICY IF EXISTS shop_orders_select ON public.shop_orders;
CREATE POLICY shop_orders_select ON public.shop_orders
  FOR SELECT TO authenticated
  USING (user_id = auth.uid() OR public.shop_is_admin());

DROP POLICY IF EXISTS shop_orders_insert_own ON public.shop_orders;
CREATE POLICY shop_orders_insert_own ON public.shop_orders
  FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS shop_orders_admin_update ON public.shop_orders;
CREATE POLICY shop_orders_admin_update ON public.shop_orders
  FOR UPDATE TO authenticated USING (public.shop_is_admin()) WITH CHECK (public.shop_is_admin());

DROP POLICY IF EXISTS shop_order_items_select ON public.shop_order_items;
CREATE POLICY shop_order_items_select ON public.shop_order_items
  FOR SELECT TO authenticated
  USING (EXISTS (SELECT 1 FROM public.shop_orders o
                 WHERE o.id = order_id AND (o.user_id = auth.uid() OR public.shop_is_admin())));

DROP POLICY IF EXISTS shop_order_items_insert_own ON public.shop_order_items;
CREATE POLICY shop_order_items_insert_own ON public.shop_order_items
  FOR INSERT TO authenticated
  WITH CHECK (EXISTS (SELECT 1 FROM public.shop_orders o
                      WHERE o.id = order_id AND o.user_id = auth.uid()));

-- 9. ★GameStore 게임 8개 — 상품 표가 비어 있을 때만 넣습니다
--    순서는 사이트의 인기 순위(#1~#8)와 같다. price 는 정가, sale 은 할인율(%)
INSERT INTO public.shop_products (name, name_ko, developer, category, price, sale, stock, image_url)
SELECT v.name, v.name_ko, v.developer, v.category, v.price, v.sale, v.stock, v.image_url
FROM (VALUES
  ('Stardew Valley',   '스타듀 밸리',     'ConcernedApe',     '시뮬레이션', 16000, 30, 9999, 'img/cover-stardew.png'),
  ('Hollow Knight',    '할로우 나이트',   'Team Cherry',      '액션',       16500, 50, 9999, 'img/cover-hollow.png'),
  ('ELDEN RING',       '엘든 링',         'FromSoftware',     'RPG',        64800,  0, 9999, 'img/cover-eldenring.png'),
  ('Baldur''s Gate 3', '발더스 게이트 3', 'Larian Studios',   'RPG',        66000,  0, 9999, 'img/cover-bg3.png'),
  ('Cyberpunk 2077',   '사이버펑크 2077', 'CD PROJEKT RED',   'RPG',        66000, 50, 9999, 'img/cover-cyberpunk.png'),
  ('Hades',            '하데스',          'Supergiant Games', '액션',       26000, 40, 9999, 'img/cover-hades.png'),
  ('Terraria',         '테라리아',        'Re-Logic',         '샌드박스',   10500,  0, 9999, 'img/cover-terraria.png'),
  ('Lethal Company',   '리썰 컴퍼니',     'Zeekerss',         '협동',       11000, 20, 9999, 'img/cover-lethal.png')
) AS v(name, name_ko, developer, category, price, sale, stock, image_url)
WHERE NOT EXISTS (SELECT 1 FROM public.shop_products);

-- 끝. 확인: Table Editor 에 shop_ 으로 시작하는 표 4개가 보이면 성공입니다.
--
-- [관리자 지정] 쇼핑몰에서 내 계정으로 가입한 뒤, 아래 한 줄의 이메일을 내 것으로 바꿔 따로 실행합니다.
--   UPDATE public.shop_profiles SET role = 'admin' WHERE email = '내이메일@example.com';
