SELECT
    C.customer_id,
    C.customer_name,
    C.email,
    TotalSpent.total_spent,
    MostPurchasedCategory.category AS most_purchased_category
FROM
    Customers C
JOIN
    (
        SELECT
            O.customer_id,
            SUM(OI.quantity * OI.price_per_unit) AS total_spent
        FROM
            Orders O
        JOIN
            Order_Items OI ON O.order_id = OI.order_id
        WHERE
            O.order_date >= CURDATE() - INTERVAL 1 YEAR
        GROUP BY
            O.customer_id
    ) AS TotalSpent ON C.customer_id = TotalSpent.customer_id
JOIN
    (
        SELECT
            O.customer_id,
            P.category,
            SUM(OI.quantity * OI.price_per_unit) AS category_spent
        FROM
            Orders O
        JOIN
            Order_Items OI ON O.order_id = OI.order_id
        JOIN
            Products P ON OI.product_id = P.product_id
        WHERE
            O.order_date >= CURDATE() - INTERVAL 1 YEAR
        GROUP BY
            O.customer_id, P.category
    ) AS MostPurchasedCategory ON TotalSpent.customer_id = MostPurchasedCategory.customer_id
GROUP BY
    C.customer_id
ORDER BY
    TotalSpent.total_spent DESC
LIMIT 5;