package jump61;

/** An automated Player.
 *  @author Daniel Wong
 */
class AI extends Player {

    /** Time allotted to all but final search depth (milliseconds). */
    private static final long TIME_LIMIT = 15000;

    /** Number of calls to minmax between checks of elapsed time. */
    private static final long TIME_CHECK_INTERVAL = 10000;

    /** Number of milliseconds in one second. */
    private static final double MILLIS = 1000.0;

    /** A new player of GAME initially playing COLOR that chooses
     *  moves automatically.
     */
    AI(Game game, Side color) {
        super(game, color);
    }

    /** Makes a random move. This method was for testing
    * purposes only and should never be called. */
    void makeRandomMove() {
        int[] moves = getRandomMove();
        int r = moves[0];
        int c = moves[1];
        getGame().makeMove(r, c);
        System.out.println("Random move made.");
        getGame().reportMove(getSide(), r, c);
    }

    /** For testing purposes only. Returns an int[] that
     * represents a random move with
     * index 0 corresponding to row and index 1 corresponding
     * to column. */
    int[] getRandomMove() {
        int r; int c;
        int size = getBoard().size();
        r = 1 + getGame().randInt(size);
        c = 1 + getGame().randInt(size);
        while (!getBoard().isLegal(getSide(), r, c)) {
            r = 1 + getGame().randInt(size);
            c = 1 + getGame().randInt(size);
        }
        int[] moves = new int[2];
        moves[0] = r;
        moves[1] = c;
        return moves;
    }

    @Override
    void makeMove() {
        int max = Integer.MIN_VALUE;
        int bestr = -1;
        int bestc = -1;
        int val = Integer.MIN_VALUE;
        for (int r = 1; r < getGame().getBoard().size() + 1; r++) {
            for (int c = 1; c < getGame().getBoard().size() + 1; c++) {
                if (getGame().getBoard().isLegal(getSide(), r, c)) {
                    Board copy = new MutableBoard(getGame().getBoard());
                    copy.addSpot(getSide(), r, c);
                    if (getGame().getBoard().size() < 3) {
                        val = minmax(getSide(),
                            copy, 1, Integer.MAX_VALUE);
                    } else {
                        val = minmax(getSide(),
                            copy, 4, Integer.MAX_VALUE);
                    }
                    if (val > max) {
                        bestr = r;
                        bestc = c;
                        max = val;
                    }
                }
            }
        }
        if (max == Integer.MIN_VALUE) {
            int[] randomMove = getRandomMove();
            bestr = randomMove[0];
            bestc = randomMove[1];
        }
        if (getGame().getBoard().size() < 3
            && getGame().getBoard().get(1, 1).getSide() == Side.RED
            && getGame().getBoard().numOfSide(Side.BLUE) == 0) {
            bestr = 2;
            bestc = 2;
        }
        getGame().reportMove(getSide(), bestr, bestc);
        getGame().makeMove(bestr, bestc);
    }

    /** Return the minimum of CUTOFF and the minmax value of board B
     *  (which must be mutable) for player P to a search depth of D
     *  (where D == 0 denotes statically evaluating just the next move).
     *  The contents of B are
     *  invariant over this call. */
    private int minmax(Side p, Board b, int d, int cutoff) {
        if (b.numOfSide(p) == b.size() * b.size()) {
            return b.size() * b.size();
        }
        if (b.numOfSide(p.opposite()) == b.size() * b.size()) {
            return Integer.MIN_VALUE;
        }
        if (d == 0) {
            return staticEval(p, b);
        }
        int bestSoFar = Integer.MIN_VALUE;
        for (int r = 1; r < b.size() + 1; r++) {
            for (int c = 1; c < b.size() + 1; c++) {
                MutableBoard copy = new MutableBoard(b);
                copy.addSpot(p, r, c);
                int response = minmax(p.opposite(),
                    copy, d - 1, -1 * cutoff);
                if (-1 * response > bestSoFar) {
                    bestSoFar = -1 * response;
                }
                if (response < cutoff) {
                    cutoff = response;
                }
                if (-1 * response >= cutoff) {
                    break;
                }
            }
        }
        return bestSoFar;
    }

    /** Returns heuristic value of board B for player P.
     *  Higher is better for P. */
    private int staticEval(Side p, Board b) {
        int value = b.numOfSide(p) - b.numOfSide(p.opposite());
        return value;
    }

}
