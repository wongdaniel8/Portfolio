package jump61;

import static jump61.Side.*;

import org.junit.Test;
import static org.junit.Assert.*;
import java.util.ArrayList;

/** Unit tests of Boards.
 *  @author Daniel Wong
 */
public class BoardTest {

    private static final String NL = System.getProperty("line.separator");

    @Test
    public void testIllegalMoves() {
        MutableBoard B = new MutableBoard(2);
        assertEquals(B.whoseMove(), RED);
        assertEquals(B.isLegal(RED), true);
        assertEquals(B.isLegal(BLUE), false);
        assertEquals(B.isLegal(RED, 1, 1), true);
        assertEquals(B.isLegal(BLUE, 1, 1), true);
        B.addSpot(RED, 1, 1);
        assertEquals(B.whoseMove(), BLUE);
        assertEquals(B.isLegal(BLUE, 1, 1), false);
        B.addSpot(BLUE, 2, 1);
        assertEquals(B.isLegal(RED, 2, 1), false);
    }

    @Test
    public void addSpotInfiniteRecursion() {
        MutableBoard B = new MutableBoard(2);
        B.addSpot(RED, 1, 1);
        B.addSpot(BLUE, 2, 1);
        B.addSpot(RED, 1, 2);
        B.addSpot(BLUE, 2, 2);
        B.addSpot(RED, 1, 1);
        assertEquals(B.numOfSide(RED), 4, .01);
    }

    @Test
    public void testGetValidNeighborCoords() {
        MutableBoard B = new MutableBoard(5);
        ArrayList<int[]> coords = B.getValidNeighborCoords(1, 1);
        assertEquals(coords.size(), 2, .01);
        for (int[] a : coords) {
            System.out.print(a[0] + " " + a[1] + ", ");
        }
        System.out.println();
        ArrayList<int[]> coords1 = B.getValidNeighborCoords(2, 2);
        assertEquals(coords1.size(), 4, .01);
        for (int[] a : coords1) {
            System.out.print(a[0] + " " + a[1] + ", ");
        }
        System.out.println();
        ArrayList<int[]> coords2 = B.getValidNeighborCoords(1, 2);
        assertEquals(coords2.size(), 3, .01);
        for (int[] a : coords2) {
            System.out.print(a[0] + " " + a[1] + ", ");
        }
    }

    /* Tests clear(), numPieces(), and equals(). **/
    @Test
    public void testMiscellaneous() {
        MutableBoard B = new MutableBoard(2);
        B.addSpot(RED, 1, 1);
        B.addSpot(BLUE, 2, 1);
        B.addSpot(RED, 1, 2);
        assertEquals(B.numPieces(), 7, .01);
        assertEquals(B.get(1, 1), B.get(1, 2));
        B.clear(3);
        MutableBoard C = new MutableBoard(3);
        assertEquals(B.equals(C), true);
        assertEquals(B.numPieces(), 9, .01);
        assertEquals(B.numOfSide(WHITE), 9, .01);
        assertEquals(B.size(), 3, .01);
    }

    @Test
    public void testSize() {
        Board B = new MutableBoard(5);
        assertEquals("bad length", 5, B.size());
        ConstantBoard C = new ConstantBoard(B);
        assertEquals("bad length", 5, C.size());
        Board D = new MutableBoard(C);
        assertEquals("bad length", 5, C.size());
    }

    @Test
    public void testSet() {
        Board B = new MutableBoard(5);
        B.set(2, 2, 1, RED);
        assertEquals("wrong number of spots", 1, B.get(2, 2).getSpots());
        assertEquals("wrong color", RED, B.get(2, 2).getSide());
        assertEquals("wrong count", 1, B.numOfSide(RED));
        assertEquals("wrong count", 0, B.numOfSide(BLUE));
        assertEquals("wrong count", 24, B.numOfSide(WHITE));
    }
    @Test
    public void testMove() {
        Board B = new MutableBoard(6);
        checkBoard("#0", B);
        B.addSpot(RED, 1, 1);
        checkBoard("#1", B, 1, 1, 2, RED);
        B.addSpot(BLUE, 2, 1);
        checkBoard("#2", B, 1, 1, 2, RED, 2, 1, 2, BLUE);
        B.addSpot(RED, 1, 1);
        checkBoard("#3", B, 1, 1, 1, RED, 2, 1, 3, RED, 1, 2, 2, RED);
        B.undo();
        checkBoard("#2U", B, 1, 1, 2, RED, 2, 1, 2, BLUE);
        B.undo();
        checkBoard("#1U", B, 1, 1, 2, RED);
        B.undo();
        checkBoard("#0U", B);
    }

    /** Checks that B conforms to the description given by CONTENTS.
     *  CONTENTS should be a sequence of groups of 4 items:
     *  r, c, n, s, where r and c are row and column number of a square of B,
     *  n is the number of spots that are supposed to be there and s is the
     *  color (RED or BLUE) of the square.  All squares not listed must
     *  be WHITE with one spot.  Raises an exception signaling a unit-test
     *  failure if B does not conform. */
    private void checkBoard(String msg, Board B, Object... contents) {
        for (int k = 0; k < contents.length; k += 4) {
            String M = String.format("%s at %d %d", msg, contents[k],
                                     contents[k + 1]);
            assertEquals(M, (int) contents[k + 2],
                         B.get((int) contents[k],
                               (int) contents[k + 1]).getSpots());
            assertEquals(M, contents[k + 3],
                         B.get((int) contents[k],
                               (int) contents[k + 1]).getSide());
        }
        int c;
        c = 0;
        for (int i = B.size() * B.size() - 1; i >= 0; i -= 1) {
            assertTrue("bad white square #" + i,
                       (B.get(i).getSide() != WHITE)
                       || (B.get(i).getSpots() == 1));
            if (B.get(i).getSide() != WHITE) {
                c += 1;
            }
        }
        assertEquals("extra squares filled", contents.length / 4, c);
    }

}
