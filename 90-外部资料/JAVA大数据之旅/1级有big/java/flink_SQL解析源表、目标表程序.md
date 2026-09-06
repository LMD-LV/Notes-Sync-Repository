pom.xml:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <groupId>org.example</groupId>
    <artifactId>stream_etl</artifactId>
    <properties>
        <flink.major.version>1.14</flink.major.version>
        <flink.minor.version>6</flink.minor.version>
        <flink.version>${flink.major.version}.${flink.minor.version}</flink.version>
        <flink.scala.version>2.11</flink.scala.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java_${flink.scala.version}</artifactId>
            <version>${flink.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients_${flink.scala.version}</artifactId>
            <version>${flink.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-runtime-web_${flink.scala.version}</artifactId>
            <version>${flink.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-planner_${flink.scala.version}</artifactId>
            <version>${flink.version}</version>
        </dependency>  
    </dependencies>
  
</project>
```

源码：

```java
package com.demo.stream.sql;

import org.apache.calcite.avatica.util.Casing;
import org.apache.calcite.avatica.util.Quoting;
import org.apache.calcite.sql.*;
import org.apache.calcite.sql.parser.SqlParser;
import org.apache.calcite.sql.util.SqlBasicVisitor;
import org.apache.flink.sql.parser.dml.RichSqlInsert;
import org.apache.flink.sql.parser.impl.FlinkSqlParserImpl;
import org.apache.flink.sql.parser.validate.FlinkSqlConformance;

import java.util.HashSet;
import java.util.Set;

public class SqlVisitorTest {

    public static void main(String[] args) throws Exception {
        /*
            写insert into select 或者 select类型的SQL在这里,解析出所有的输出和输入表名
            不一定是可运行的,只要符合flink SQL规范就行，写个不存在的字段和表都可以
         */
        String sql = "";

        SqlParser sqlParser = SqlParser.create(sql,
                                               SqlParser.config()
                                               .withCaseSensitive(true)
                                               .withQuoting(Quoting.BACK_TICK)
                                               .withParserFactory(FlinkSqlParserImpl.FACTORY)
                                               .withUnquotedCasing(Casing.TO_LOWER)
                                               .withQuotedCasing(Casing.UNCHANGED)
                                               .withConformance(FlinkSqlConformance.DEFAULT)
                                              );
        SqlNodeList nodeList = sqlParser.parseStmtList();
        SqlNode node = nodeList.get(0);
        FlinkTableVisitor testVisitor = new FlinkTableVisitor();
        node.accept(testVisitor);
        //打印输出的表
        System.out.println(testVisitor.tables.toString());

    }

    /**
     * 表信息
     */
    public static class SqlTables {
        /**
         * 输入表
         */
        private Set<String> sourceTables = new HashSet<>();
        /**
         * 输出表
         */
        private String sinkTable;

        public Set<String> getSourceTables() {
            return sourceTables;
        }

        public void setSourceTables(Set<String> sourceTables) {
            this.sourceTables = sourceTables;
        }

        public void setSinkTable(String sinkTable) {
            this.sinkTable = sinkTable;
        }

        @Override
        public String toString() {
            return "SqlTables{" +
            "sourceTables=" + sourceTables +
            ", sinkTable='" + sinkTable + '\'' +
            '}';
        }
    }

    private static class FlinkTableVisitor extends SqlBasicVisitor<SqlTables> {

        private final SqlTables tables;

        FlinkTableVisitor() {
            this.tables = new SqlTables();
        }

        public SqlTables visitSelect(SqlSelect select) {
            SqlNode from = select.getFrom();
            if (from instanceof SqlSelect) {
                return this.visitSelect((SqlSelect) from);
            } else if (from instanceof SqlIdentifier) {
                this.tables.sourceTables.add(from.toString());
                return this.tables;
            } else {
                return super.visit(select);
            }
        }

        public SqlTables visitJoin(SqlJoin join) {
            this.visitJoinNode(join.getLeft());
            this.visitJoinNode(join.getRight());
            return this.tables;
        }

        public SqlTables visitJoinNode(SqlNode node) {
            if (node instanceof SqlCall) {
                SqlCall call = (SqlCall) node;
                if (call.getOperator().getKind() == SqlKind.AS) {
                    SqlNode s = call.getOperandList().get(0);
                    if (s instanceof SqlIdentifier) {
                        this.tables.sourceTables.add(s.toString());
                    } else {
                        s.accept(this);
                    }
                } else {
                    this.visit(call);
                }
            } else if (node instanceof SqlIdentifier) {
                this.tables.sourceTables.add(node.toString());
            }
            return this.tables;
        }

        public SqlTables visit(SqlCall call) {
            if (call instanceof RichSqlInsert) {
                RichSqlInsert insert = (RichSqlInsert) call;
                this.tables.sinkTable = insert.getTargetTable().toString();
                insert.getSource().accept(this);
            } else if (call instanceof SqlSelect) {
                return this.visitSelect((SqlSelect) call);
            } else if (call instanceof SqlJoin) {
                SqlJoin join = (SqlJoin) call;
                return this.visitJoin(join);
            } else if (call.getOperator().getKind() == SqlKind.AS) {
                call.getOperandList().get(0).accept(this);
                return this.tables;
            } else if (call.getOperator().getKind() == SqlKind.SNAPSHOT) {
                SqlSnapshot snapshot = (SqlSnapshot) call;
                SqlNode tableRef = snapshot.getTableRef();
                if (tableRef instanceof SqlIdentifier) {
                    this.tables.sourceTables.add(tableRef.toString());
                } else {
                    tableRef.accept(this);
                }
                return this.tables;
            } else if (call.getOperator().getKind() == SqlKind.TABLE_REF) {
                SqlTableRef tableRef = (SqlTableRef) call;
                this.tables.sourceTables.add(tableRef.getOperandList().get(0).toString());
                return this.tables;
            }
            return super.visit(call);
        }
    }

}

```

应用场景

1.扫描出所有所有用到的表，删除未用到的表（程序扫出来的表一定是用到的，剩下没用的表可人工检查，减少工作量）

2.构建表一级的依赖关系图