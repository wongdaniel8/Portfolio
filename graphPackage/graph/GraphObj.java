package graph;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.ArrayList;


/* See restrictions in Graph.java. */

/** A partial implementation of Graph containing elements common to
 *  directed and undirected graphs.
 *
 *  @author Daniel Wong
 */
abstract class GraphObj extends Graph {

    /** A new, empty Graph. */
    GraphObj() {
        _vertices = new HashMap<Integer, LinkedList<Integer>>();
        _predecessorMap = new HashMap<Integer, LinkedList<Integer>>();
    }

    @Override
    public int vertexSize() {
        return _vertices.size();
    }

    @Override
    public int maxVertex() {
        int max = 0;
        for (Integer i : _vertices.keySet()) {
            if (i > max) {
                max = i;
            }
        }
        return max;
    }

    @Override
    public int edgeSize() {
        int count = 0;
        for (Integer i :_vertices.keySet()) {
            count += _vertices.get(i).size();
        }
        if (!isDirected()) {
            count += _selfEdges;
            return count / 2;
        } else {
            return count;
        }
    }

    @Override
    public abstract boolean isDirected();

    @Override
    public int outDegree(int v) {
        if (!contains(v)) {
            return 0;
        }
        return _vertices.get(v).size();
    }

    @Override
    public int inDegree(int v) {
        if (!contains(v)) {
            return 0;
        }
        if (isDirected()) {
            int count = 0;
            for (Integer i : _vertices.keySet()) {
                for (Integer i2 : _vertices.get(i)) {
                    if (i2 == v) {
                        count++;
                    }
                }
            }
            return count;
        } else {
            return outDegree(v);
        }
    }

    @Override
    public boolean contains(int u) {
        return _vertices.containsKey(u);
    }

    @Override
    public boolean contains(int u, int v) {
        if (!contains(u) || !contains(v)) {
            return false;
        }
        for (Integer i : _vertices.get(u)) {
            if (v == i) {
                return true;
            }
        }
        if (!isDirected()) {
            for (Integer i : _vertices.get(v)) {
                if (u == i) {
                    return true;
                }
            }
        }
        return false;
    }

    @Override
    public int add() {
        int i = 1;
        while (true) {
            if (!contains(i)) {
                LinkedList<Integer> myList = new LinkedList<Integer>();
                _vertices.put(i, myList);
                LinkedList<Integer> myPredecessorList =
                    new LinkedList<Integer>();
                _predecessorMap.put(new Integer(i), myPredecessorList);
                break;
            } else {
                i++;
            }
        }
        return i;
    }

    @Override
    public int add(int u, int v) {
        if (contains(u, v)) {
            return u;
        }
        if (u == v) {
            _selfEdges += 1;
            _vertices.get(u).add(v);
            _predecessorMap.get(v).add(new Integer(u));
            return u;
        } else {
            _vertices.get(u).add(v);
            _predecessorMap.get(v).add(new Integer(u));
            if (!isDirected()) {
                _vertices.get(v).add(u);
                _predecessorMap.get(u).add(new Integer(v));
            }
        }
        return u;
    }

    @Override
    public void remove(int v) {
        if (contains(v)) {
            for (Integer i : _vertices.keySet()) {
                if (_vertices.get(i).contains(v)) {
                    _vertices.get(i).remove((Integer) v);
                }
            }
            _vertices.remove(v);
        }
        if (_predecessorMap.containsKey(v)) {
            for (Integer i : _predecessorMap.keySet()) {
                if (_predecessorMap.get(i).contains(v)) {
                    _predecessorMap.get(i).remove((Integer) v);
                }
            }
            _predecessorMap.remove(v);
        }
    }

    @Override
    public void remove(int u, int v) {
        if (contains(u, v)) {
            _vertices.get(u).remove((Integer) v);
            if (!isDirected() && u != v) {
                _vertices.get(v).remove((Integer) u);
            }
        }

        if (containsForPredecessorMap(u, v)) {
            _predecessorMap.get(u).remove((Integer) v);
            if (!isDirected() && u != v) {
                _predecessorMap.get(v).remove((Integer) u);
            }
        }
    }

    /** My method that returns true if V is a predecessor of U. */
    private boolean containsForPredecessorMap(int u, int v) {
        if (!_predecessorMap.containsKey(u)
            || !_predecessorMap.containsKey(v)) {
            return false;
        }
        for (Integer i : _predecessorMap.get(u)) {
            if (v == i) {
                return true;
            }
        }
        if (!isDirected()) {
            for (Integer i : _predecessorMap.get(v)) {
                if (u == i) {
                    return true;
                }
            }
        }
        return false;
    }

    @Override
    public Iteration<Integer> vertices() {
        ArrayList<Integer> array = new ArrayList<Integer>();
        for (Integer i : _vertices.keySet()) {
            array.add(i);
        }
        Iteration<Integer> returnval = Iteration.iteration(array.iterator());
        return returnval;
    }

    @Override
    public int successor(int v, int k) {
        if (!contains(v) || k < 0 || (k > _vertices.get(v).size() - 1)) {
            return 0;
        } else {
            return _vertices.get(v).get(k);
        }
    }

    @Override
    public int predecessor(int v, int k) {
        if (!_predecessorMap.containsKey(v) || k < 0
            || k > _predecessorMap.get(v).size() - 1) {
            return 0;
        } else {
            return _predecessorMap.get(v).get(k);
        }
    }

    @Override
    public Iteration<Integer> successors(int v) {
        if (!contains(v)) {
            ArrayList<Integer> empty = new ArrayList<Integer>();
            Iteration<Integer> returnEmpty
                = Iteration.iteration(empty.iterator());
            return returnEmpty;
        }
        ArrayList<Integer> array = new ArrayList<Integer>();
        int k = _vertices.get(v).size() - 1; int i = 0;
        while (i <= k) {
            array.add(successor(v, i));
            i++;
        }
        Iteration<Integer> returnval = Iteration.iteration(array.iterator());
        return returnval;
    }

    @Override
    public Iteration<Integer> predecessors(int v) {
        if (!contains(v)) {
            ArrayList<Integer> empty = new ArrayList<Integer>();
            Iteration<Integer> returnEmpty
                = Iteration.iteration(empty.iterator());
            return returnEmpty;
        }
        ArrayList<Integer> array = new ArrayList<Integer>();
        int k = _predecessorMap.get(v).size() - 1; int i = 0;
        while (i <= k) {
            array.add(predecessor(v, i));
            i++;
        }
        Iteration<Integer> returnval = Iteration.iteration(array.iterator());
        return returnval;
    }


    @Override
    public Iteration<int[]> edges() {
        ArrayList<int[]> array = new ArrayList<int[]>();
        for (Integer i : _vertices.keySet()) {
            for (int j = 0; j < _vertices.get(i).size(); j++) {
                int[] element = new int[2];
                element[0] = i;
                element[1] = _vertices.get(i).get(j);
                int[] reverse = new int[2];
                reverse[0] = element[1];
                reverse[1] = element[0];
                if (!isDirected() && !specialContains(element, array)
                    && !specialContains(reverse, array)) {
                    array.add(element);
                }
                if (isDirected()) {
                    array.add(element);
                }
            }
        }
        Iteration<int[]> returnval = Iteration.iteration(array.iterator());
        return returnval;
    }

    /** Returns true if, given an array A and an ArrayList of int arrays ARRAY,
     * A is contained within ARRAY. */
    private boolean specialContains(int[] a, ArrayList<int[]> array) {
        for (int[] element : array) {
            if ((a[0] == element[0]) && (a[1] == element[1])) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected boolean mine(int v) {
        return contains(v);
    }

    @Override
    protected void checkMyVertex(int v) {
        if (!contains(v)) {
            throw new IllegalArgumentException();
        }
    }

    @Override
    protected int edgeId(int u, int v) {
        int id;
        if (!contains(u, v)) {
            return 0;
        } else {
            if (!isDirected()) {
                int min = Math.min(u, v);
                int max = Math.max(u, v);
                String minPrime = Integer.toString(min);
                String maxPrime = Integer.toString(max);
                String concat1 = minPrime + maxPrime;
                id = Integer.parseInt(concat1);
            } else {
                String uprime = Integer.toString(u);
                String vprime = Integer.toString(v);
                String concat = uprime + vprime;
                id = Integer.parseInt(concat);
            }
            return id;
            
        }
    }

    /** HashMap in which the buckets are vertices,
     * and the following linkedList is a
     * a list of successors. */
    private HashMap<Integer, LinkedList<Integer>> _vertices;

    /** HashMap in which buckets are vertices,
     * and the following LinkedList is a list
     * of predecessors. */
    private HashMap<Integer, LinkedList<Integer>> _predecessorMap;
    /** Number of selfEdges in me. */
    private int _selfEdges;
}
