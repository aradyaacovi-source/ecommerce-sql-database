-- Analysis queries (Task 1)
-- Source: the team's original Part 3 SQL file, split into separate files for this repository.
-- Hebrew comments are original; "-- EN:" lines are English translations added for readers.

-- ============================================================
-- Part 3 SQL - Zales Jewelry Database - Group 18
-- ============================================================

USE zales;

-- ============================================================
-- מטלה 1 — שאילתות
-- EN: Task 1 - Queries
-- ============================================================

-- שאילתה 1: לקוחות VIP — GROUP BY / HAVING
-- EN: Query 1: VIP customers (NY/CA, >3 items in 2024) - GROUP BY / HAVING
SELECT C.Email, C.Name_First, C.Name_Last, SUM(I.Quantity) AS Total_Items
FROM CUSTOMERS AS C
JOIN ORDERS_TABLE AS O ON C.Email = O.Email
JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
WHERE O.Address_State IN ('NEW YORK', 'CALIFORNIA')
  AND YEAR(O.Date) = 2024
GROUP BY C.Email, C.Name_First, C.Name_Last
HAVING SUM(I.Quantity) > 3
ORDER BY Total_Items DESC;

-- ============================================================

-- שאילתה 2א: קטגוריות מעל 10% מסך המכירות — מקוננת ב-HAVING
-- EN: Query 2a: categories above 10% of total units sold - subquery in HAVING
SELECT J.Category, SUM(I.Quantity) AS Total_Category_Qty
FROM JEWELRY AS J
JOIN JEWELRY_VARIANTS AS JV ON J.Jewelry = JV.Jewelry
JOIN INCLUDES AS I ON JV.Jewelry_Variant = I.Jewelry_Variant
GROUP BY J.Category
HAVING SUM(I.Quantity) > (SELECT SUM(Quantity) * 0.10 FROM INCLUDES);

-- ============================================================

-- שאילתה 2ב: לקוחות עם ממוצע פריטים להזמנה מעל 3 — מקוננת ב-FROM
-- EN: Query 2b: customers averaging more than 3 items per order - subquery in FROM
SELECT C.Name_First, C.Name_Last, AVG(Order_Totals.Total_Items) AS Avg_Items_Per_Order
FROM CUSTOMERS AS C
JOIN (
    SELECT O.Email, O.Order_ID, SUM(I.Quantity * 1.0) AS Total_Items
    FROM ORDERS_TABLE AS O
    JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
    GROUP BY O.Email, O.Order_ID
) AS Order_Totals ON C.Email = Order_Totals.Email
GROUP BY C.Email, C.Name_First, C.Name_Last
HAVING AVG(Order_Totals.Total_Items) > 3;

-- ============================================================

-- שאילתה 3: Window Functions — מספר סידורי, ימים בין רכישות, LTV מצטבר
-- EN: Query 3: window functions - order sequence, days between purchases, cumulative LTV
SELECT
    O.Email,
    O.Date,
    ROW_NUMBER() OVER (PARTITION BY O.Email ORDER BY O.Date) AS Order_Sequence,
    DATEDIFF(day, LAG(O.Date) OVER (PARTITION BY O.Email ORDER BY O.Date), O.Date) AS Days_Since_Last_Order,
    SUM(SUM(I.Quantity * C.Price_Addition)) OVER (PARTITION BY O.Email ORDER BY O.Date) AS Cumulative_LTV
FROM ORDERS_TABLE AS O
JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
JOIN BUILDS_FROM AS BF ON I.Jewelry_Variant = BF.Jewelry_Variant
JOIN COMPONENTS AS C ON BF.Component = C.Component
GROUP BY O.Order_ID, O.Email, O.Date
ORDER BY O.Email, O.Date;

-- ============================================================

-- שאילתה 4: CTE — לקוחות מעל ממוצע גלובלי ומעל 5,000 דולר
-- EN: Query 4: CTE - customers above the global average order value and over $5,000 lifetime value
WITH Order_Revenues AS (
    SELECT I.[Order_ID], SUM(I.Quantity * C.Price_Addition) AS Order_Total
    FROM INCLUDES AS I
    JOIN BUILDS_FROM AS BF ON I.Jewelry_Variant = BF.Jewelry_Variant
    JOIN COMPONENTS AS C ON BF.Component = C.Component
    GROUP BY I.[Order_ID]
),
Global_Avg_Revenue AS (
    SELECT AVG(Order_Total * 1.0) AS Global_Avg
    FROM Order_Revenues
),
Customer_Revenues AS (
    SELECT O.Email,
           AVG(ORev.Order_Total * 1.0) AS Personal_Avg,
           SUM(ORev.Order_Total)        AS Lifetime_Value
    FROM ORDERS_TABLE AS O
    JOIN Order_Revenues AS ORev ON O.[Order_ID] = ORev.[Order_ID]
    GROUP BY O.Email
)
SELECT CU.Name_First, CU.Name_Last, CR.Personal_Avg, CR.Lifetime_Value
FROM CUSTOMERS AS CU
JOIN Customer_Revenues AS CR ON CU.Email = CR.Email
WHERE CR.Personal_Avg > (SELECT Global_Avg FROM Global_Avg_Revenue)
  AND CR.Lifetime_Value > 5000
ORDER BY CR.Personal_Avg DESC;
