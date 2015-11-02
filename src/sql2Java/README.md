#sql2Java

Generate data access code in java. Include:

- Entity
- Mapper
- Dao
- jqGridColumn


## Usage


1. Fill `sql.txt` with sql script that only contains field declare statement. 
 
    ```
    id int(8) not null primary key auto_increment,
    rec_algorithm_test_id int(8) not null,
    package_name char(100) not null,
    package_title char(255) not null,
    package_icon Text not null,
    package_info Text not null,
    partin_num TINYINT not null,
    score float not null,
    create_by char(50) not null,
    create_datetime datetime not null,
    update_datetime datetime not null
    ```
2. Launch `sql2Java.py`
3. Get result in sub directory `result`. There will list follow files:

    - %name%.java
    - %name%Dao.java
    - %name%Mapper.java
    - %name%.jqgrid.txt