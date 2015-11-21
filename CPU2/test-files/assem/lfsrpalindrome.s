    LfsrBitpal:
        addiu $sp, $sp, -4
        sw $ra, 0($sp) 
    	lui $a0, 0x01FF
    	ori $a0, $a0, 0xFE00
        add $t0, $0, $a0
    LFSR:
        lfsr $t1, $t0
        srl $t0, $t0, 1 
        sll $t1, $t1, 31 
        or $t0, $t0, $t1
        beq $t0, $a0, no_palindrome
        bitpal $t2, $t0 
        addiu $t3, $0, 1
        bne $t2, $t3, LFSR
        add $v0, $0, $t0
        addiu $a0, $t0, 0
        lw $ra, 0($sp) 
        addiu $sp, $sp, 4
        jr $ra
    no_palindrome:
        add $v0, $0, $a0
        lw $ra, 0($sp) 
        addiu $sp, $sp, 4
        jr $ra
