package db61b;
import java.util.TreeMap;

/** A collection of Tables, indexed by name.
 *  @author Daniel Wong */
class Database {
    /** An empty database. */
    public Database() {
        map = new TreeMap<String, Table>();
    }

    /** Return the Table whose name is NAME stored in this database, or null
     *  if there is no such table. */
    public Table get(String name) {
        return map.get(name);
    }

    /** Set or replace the table named NAME in THIS to TABLE.  TABLE and
     *  NAME must not be null, and NAME must be a valid name for a table. */
    public void put(String name, Table table) {
        if (name == null || table == null) {
            throw new IllegalArgumentException("null argument");
        } else {
            map.put(name, table);
        }
    }
    /** My map. */
    private TreeMap<String, Table> map;
}
