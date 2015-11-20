// This file contains a SUGGESTION for the structure of your program.  You
// may change any of it, or add additional files to this directory (package),
// as long as you conform to the project specification.

// Comments that start with "//" are intended to be removed from your
// solutions.
package jump61;

import static jump61.Side.*;
import static jump61.Square.square;

/** A Jump61 board state that may be modified.
 *  @author
 */
class MutableBoard extends Board {

    /** An N x N board in initial configuration. */
    MutableBoard(int N) {
        // FIXME
    }

    /** A board whose initial contents are copied from BOARD0, but whose
     *  undo history is clear. */
    MutableBoard(Board board0) {
        // FIXME
    }

    @Override
    void clear(int N) {
        // FIXME
        announce();
    }

    @Override
    void copy(Board board) {
        // FIXME
    }

    /** Copy the contents of BOARD into me, without modifying my undo
     *  history.  Assumes BOARD and I have the same size. */
    private void internalCopy(MutableBoard board) {
        // FIXME
    }

    @Override
    int size() {
        // REPLACE WITH SOLUTION
        return 0;
    }

    @Override
    Square get(int n) {
        // REPLACE WITH SOLUTION
        return null;
    }

    @Override
    int numOfSide(Side side) {
        // REPLACE WITH SOLUTION
        return 0;
    }

    @Override
    int numPieces() {
        // REPLACE WITH SOLUTION
        return 0;
    }

    @Override
    void addSpot(Side player, int r, int c) {
        // FIXME
        announce();
    }

    @Override
    void addSpot(Side player, int n) {
        // FIXME
        announce();
    }

    @Override
    void set(int r, int c, int num, Side player) {
        internalSet(sqNum(r, c), square(player, num));
    }

    @Override
    void set(int n, int num, Side player) {
        internalSet(n, square(player, num));
        announce();
    }

    @Override
    void undo() {
        // FIXME
    }

    /** Record the beginning of a move in the undo history. */
    private void markUndo() {
        // FIXME
    }

    /** Set the contents of the square with index IND to SQ. Update counts
     *  of numbers of squares of each color.  */
    private void internalSet(int ind, Square sq) {
        // FIXME
    }

    /** Notify all Observers of a change. */
    private void announce() {
        setChanged();
        notifyObservers();
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof MutableBoard)) {
            return obj.equals(this);
        } else {
            // REPLACE WITH SOLUTION
            return false;
        }
    }

    @Override
    public int hashCode() {
        // REPLACE WITH SOLUTION.  RETURN A NUMBER THAT IS THE SAME FOR BOARDS
        // WITH IDENTICAL CONTENTS (IT NEED NOT BE DIFFERENT IF THE BOARDS
        // DIFFER.)  THE CURRENT STATEMENT WORKS, BUT IS NOT PARTICULARLY
        // EFFICIENT.
        return 0;
    }

}
