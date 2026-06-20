-- ============================================================
-- Oracle 抽出テンプレ(列を「標準概念名」にエイリアスする = 取得時にマッピング完了)
-- テーブル名・列名は仮置き。自社スキーマに合わせて置換してください。
-- リアルタイム: SYSDATE 基準で絞れば実行ごとに最新値。
-- ============================================================

-- (1) 日次 計画/実績/良品/不良  -> 製造三角図・達成率・OEE品質・流動数曲線
SELECT TRUNC(d.prod_date)        AS "日付",
       d.line_cd                 AS "ライン",
       d.item_cd                 AS "機種",
       d.plan_qty                AS "計画数",
       d.actual_qty              AS "実績数",
       d.good_qty                AS "良品数",
       d.ng_qty                  AS "不良数",
       d.input_qty               AS "投入数"
FROM   prod_daily d
WHERE  d.prod_date >= TRUNC(SYSDATE) - 14      -- 直近14日(=ほぼリアルタイム)
ORDER  BY d.prod_date, d.item_cd;

-- (2) シリアル実績(時刻つき) -> 製造三角図(日内)・PPH・機種ズレ
SELECT s.serial_no               AS "シリアルNo",
       s.prod_ts                 AS "生産時刻",
       s.line_cd                 AS "ライン",
       s.equip_cd                AS "設備",
       s.item_cd                 AS "機種(実績)",
       s.plan_item_cd            AS "計画機種",
       CASE WHEN s.judge='NG' THEN 'NG' ELSE 'OK' END AS "判定"
FROM   prod_serial s
WHERE  s.prod_ts >= SYSDATE - 1;               -- 直近24時間

-- (3) 停止ログ -> 稼働率A・ダウンタイムPareto
SELECT t.stop_ts                 AS "開始日時",
       t.equip_cd                AS "設備",
       t.reason_txt              AS "停止理由",
       t.loss_cat                AS "区分",
       t.stop_min                AS "停止(分)"
FROM   downtime_log t
WHERE  t.stop_ts >= TRUNC(SYSDATE) - 14;

-- (4) 不良明細 -> 品質Q・発生/流出
SELECT f.prod_ts                 AS "日時",
       f.item_cd                 AS "機種",
       f.occur_process           AS "発生工程",
       f.defect_name             AS "不良項目",
       f.outflow_flag            AS "流出区分"
FROM   defect_detail f
WHERE  f.prod_ts >= TRUNC(SYSDATE) - 14;
