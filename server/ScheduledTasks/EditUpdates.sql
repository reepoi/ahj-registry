DELIMITER ;;
CREATE DEFINER=`admin`@`%` PROCEDURE `test_proc`()
BEGIN
SELECT "Hello, MySQL!";
END;

CREATE DEFINER=`admin`@`%` PROCEDURE `EditUpdates`()
BEGIN

DECLARE tname   VARCHAR(255);
DECLARE cname  VARCHAR(255);
DECLARE rowv      INT;
DECLARE nval      VARCHAR(255);
DECLARE tpk        VARCHAR(50);
DECLARE updtxt   VARCHAR(300);

DECLARE done BOOLEAN DEFAULT FALSE;

DECLARE C1 CURSOR FOR
SELECT SourceTable,SourceColumn, SourceRow,NewValue 
FROM Edit 
WHERE ReviewStatus = 'A' 
AND ApprovedBy IS NOT NULL 
AND DateEffective = CURDATE();

DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;


DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
    ROLLBACK;
END;


START TRANSACTION;

OPEN C1;
get_edit: LOOP
    FETCH NEXT FROM C1 INTO tname, cname, rowv, nval;
    IF done THEN
        LEAVE get_edit;
    END IF;

    SET tpk = GetPKName( tname );
     SET @updtxt = CONCAT('UPDATE ', tname, ' SET ', cname, ' = ', nval, ' WHERE ', tpk, ' = ', rowv);

      PREPARE stmt1 FROM @updtxt;
      EXECUTE stmt1;
      DEALLOCATE PREPARE stmt1;





END LOOP get_edit;
CLOSE C1;

    COMMIT; 

END;
