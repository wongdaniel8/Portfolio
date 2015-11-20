package db61b;
import org.junit.Test;
import java.util.ArrayList;
import static org.junit.Assert.*;

public class TestPart2 {

    /* Tests select without any conditional clauses*/
    @Test
    public void testSelect() {
        String[] cols = {"name", "SID", "age", "height", "major"};
        Table t = new Table(cols);
        String[] vals = {"Daniel", "24199291", "19", "tall", "MCB/CS"};
        String[] vals2 = {"Herb420", "1234578", "18", "short", "EECS"};
        String[] vals3 = {"Kai", "0234578", "20",
                          "short", "Music/EthnicStudies"};
        Row r1 = new Row(vals);
        Row r2 = new Row(vals2);
        Row r3 = new Row(vals3);
        t.add(r1);
        t.add(r2);
        t.add(r3);
        assertEquals(t.columns(), 5, .01);
        ArrayList<String> desiredCols = new ArrayList<String>();
        desiredCols.add("name");
        desiredCols.add("major");
        desiredCols.add("age");
        Table selected = t.select(desiredCols, null);
        assertEquals(selected.columns(), 3, .01);
        assertEquals(selected.getTitle(2), "age");
        assertEquals(selected.size(), 3, .01);
    }

    @Test
    public void testSelectWithConditions() {
        String[] cols = {"name", "SID", "age", "height", "major"};
        Table t = new Table(cols);
        String[] vals = {"Daniel", "24199291", "19", "tall", "MCB/CS"};
        String[] vals2 = {"Herb420", "1234578", "18", "short", "EECS"};
        String[] vals3 = {"Kai", "0234578", "20",
                          "short", "Music/EthnicStudies"};
        String[] vals4 = {"Oscar", "4", "19", "short", "EECS"};
        String[] vals5 = {"River", "5", "20", "short", "EthnicStudies"};
        String[] vals6 = {"Anthony", "6", "20", "intermediate", "Chemistry"};
        Row r1 = new Row(vals);
        Row r2 = new Row(vals2);
        Row r3 = new Row(vals3);
        Row r4 = new Row(vals4);
        Row r5 = new Row(vals5);
        Row r6 = new Row(vals6);
        t.add(r1);
        t.add(r2);
        t.add(r3);
        t.add(r4);
        t.add(r5);
        t.add(r6);
        Column c1 = new Column("name", t);
        Column c2 = new Column("SID", t);
        Column c3 = new Column("height", t);
        Condition cond = new Condition(c1, ">=", "Daniel");
        Condition cond2 = new Condition(c2, ">=", "1");
        Condition cond3 = new Condition(c3, "!=", "short");
        ArrayList<String> selectedCols = new ArrayList<String>();
        ArrayList<Condition> conditions = new ArrayList<Condition>();
        selectedCols.add("name");
        selectedCols.add("SID");
        selectedCols.add("height");
        conditions.add(cond);
        conditions.add(cond2);
        conditions.add(cond3);
        Table selectedTable = t.select(selectedCols, conditions);
        selectedTable.print();
        assertEquals(selectedTable.size(), 1, .01);
        assertEquals(selectedTable.findColumn("age"), -1, .01);
    }
    @Test
    public void testTwoTableSelect() {
        String[] cols = {"name", "SID", "major"};
        Table t = new Table(cols);
        String[] vals = {"Daniel1", "D1", "MCB/CS"};
        String[] vals2 = {"Herb", "H2", "EECS"};
        String[] vals3 = {"Kai", "K3", "Music"};
        String[] vals4 = {"Oscar", "O4", "EECS"};
        String[] vals5 = {"River", "R5", "English"};
        Row r1 = new Row(vals);
        Row r2 = new Row(vals2);
        Row r3 = new Row(vals3);
        Row r4 = new Row(vals4);
        Row r5 = new Row(vals5);
        t.add(r1);
        t.add(r2);
        t.add(r3);
        t.add(r4);
        t.add(r5);
        t.writeTable("myT1");
        Table t2 = new Table(new String[] {"name", "sport", "food"});
        String[] vals6 = {"Daniel2", "tennis", "asian"};
        String[] vals7 = {"Herb", "boxing", "latina"};
        String[] vals8 = {"Kai", "tennis", "american"};
        String[] vals9 = {"Oscar", "coding", "mexican"};
        String[] vals10 = {"River", "basketball", "philipina"};
        Row r6 = new Row(vals6);
        Row r7 = new Row(vals7);
        Row r8 = new Row(vals8);
        Row r9 = new Row(vals9);
        Row r10 = new Row(vals10);
        t2.add(r6);
        t2.add(r7);
        t2.add(r8);
        t2.add(r9);
        t2.add(r10);
        t2.writeTable("myT2");
        ArrayList<String> colNames = new ArrayList<String>();
        colNames.add("SID");
        colNames.add("sport");
        colNames.add("food");
        Column c1 = new Column("name", t, t2);
        Column c2 = new Column("sport", t, t2);
        Column c3 = new Column("food", t, t2);
        ArrayList<Condition> conditions = new ArrayList<Condition>();
        Condition cond1 = new Condition(c1, "!=", "Daniel1");
        Condition cond2 = new Condition(c2, "!=", "tennis");
        Condition cond3 = new Condition(c3, ">", "m");
        conditions.add(cond1);
        conditions.add(cond2);
        conditions.add(cond3);
        t.select(t2, colNames, conditions).print();
    }
    public static void main(String[] args) {
        System.exit(ucb.junit.textui.runClasses(TestPart2.class));
    }
}
