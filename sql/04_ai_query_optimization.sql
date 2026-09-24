-- Query optimization with a generative AI tool (Task 4)
-- Source: the team's original Part 3 SQL file, split into separate files for this repository.
-- Hebrew comments are original; "-- EN:" lines are English translations added for readers.
-- The team asked a course-provided ChatGPT assistant for optimization ideas, applied one, and checked
-- with EXCEPT that the original and improved queries return the same rows.

USE zales;


-- ============================================================
-- מטלה 4 — אופטימיזציה עם AI
-- EN: Task 4 - Query optimization with a generative AI tool
-- ============================================================

-- שאילתה מקורית (לפני אופטימיזציה):
-- EN: Original query (before optimization):
SELECT C.Email, C.Name_First, C.Name_Last, SUM(I.Quantity) AS Total_Items
FROM CUSTOMERS AS C
JOIN ORDERS_TABLE AS O ON C.Email = O.Email
JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
WHERE O.Address_State IN ('NEW YORK', 'CALIFORNIA')
  AND YEAR(O.Date) = 2024
GROUP BY C.Email, C.Name_First, C.Name_Last
HAVING SUM(I.Quantity) > 3
ORDER BY Total_Items DESC;

-- שאילתה משופרת (אחרי המלצת AI — החלפת YEAR() בטווח תאריכים):
-- EN: Improved query (after the AI suggestion - YEAR() replaced with a date range):
SELECT C.Email, C.Name_First, C.Name_Last, SUM(I.Quantity) AS Total_Items
FROM CUSTOMERS AS C
JOIN ORDERS_TABLE AS O ON C.Email = O.Email
JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
WHERE O.Address_State IN ('NEW YORK', 'CALIFORNIA')
  AND O.[Date] >= '2024-01-01'
  AND O.[Date] <  '2025-01-01'
GROUP BY C.Email, C.Name_First, C.Name_Last
HAVING SUM(I.Quantity) > 3
ORDER BY Total_Items DESC;

-- בדיקת זהות פלט (EXCEPT דו-כיווני):
-- EN: Output equivalence check (EXCEPT):
SELECT Email, Name_First, Name_Last, Total_Items
FROM (
    SELECT C.Email, C.Name_First, C.Name_Last, SUM(I.Quantity) AS Total_Items
    FROM CUSTOMERS AS C
    JOIN ORDERS_TABLE AS O ON C.Email = O.Email
    JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
    WHERE O.Address_State IN ('NEW YORK', 'CALIFORNIA') AND YEAR(O.Date) = 2024
    GROUP BY C.Email, C.Name_First, C.Name_Last
    HAVING SUM(I.Quantity) > 3
) AS Original
EXCEPT
SELECT C.Email, C.Name_First, C.Name_Last, SUM(I.Quantity) AS Total_Items
FROM CUSTOMERS AS C
JOIN ORDERS_TABLE AS O ON C.Email = O.Email
JOIN INCLUDES AS I ON O.Order_ID = I.Order_ID
WHERE O.Address_State IN ('NEW YORK', 'CALIFORNIA')
  AND O.[Date] >= '2024-01-01' AND O.[Date] < '2025-01-01'
GROUP BY C.Email, C.Name_First, C.Name_Last
HAVING SUM(I.Quantity) > 3;
