#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "tables.h"
#include "translate_utils.h"
#include "translate.h"

/* Writes instructions during the assembler's first pass to OUTPUT. The case
      for general instructions has already been completed, but you need to write
         code to translate the li and blt pseudoinstructions. Your pseudoinstruction
	    expansions should not have any side effects.
	       NAME is the name of the instruction, ARGS is an array of the arguments, and
	          NUM_ARGS specifies the number of items in ARGS.
		     Error checking for regular instructions are done in pass two. However, for
		        pseudoinstructions, you must make sure that ARGS contains the correct number
			   of arguments. You do NOT need to check whether the registers / label are
			      valid, since that will be checked in part two.
			         Also for li:
				     - make sure that the number is representable by 32 bits. (Hint: the number
				             can be both signed or unsigned).
					         - if the immediate can fit in the imm field of an addiu instruction, then
						         expand li into a single addiu instruction. Otherwise, expand it into
							         a lui-ori pair.
								    And for blt:
								        - your expansion should use the fewest number of instructions possible.
									   MARS has slightly different translation rules for li, and it allows numbers
									      larger than the largest 32 bit number to be loaded with li. You should follow
									         the above rules if MARS behaves differently.
										    Use fprintf() to write. If writing multiple instructions, make sure that
										       each instruction is on a different line.
										          Returns the number of instructions written (so 0 if there were any errors).
*/
unsigned write_pass_one(FILE* output, const char* name, char** args, int num_args) {
  if (strcmp(name, "li") == 0) {
     if (num_args != 2) return 0;
     long int immediate;
     int check = translate_num(&immediate, args[1], 0, 0xFFFFFFFF);
     int check2 = translate_num(&immediate, args[1], -2147483648, 0x7FFFFFFF);
     if (check == -1 && check2 == -1) return 0;
     if (immediate >= 0 && immediate <= 0x10000 || immediate >= -32768 && immediate <= 0x7FFF) {
        char* new_args[3];
        new_args[0] = args[0];
        new_args[1] = "$0";
        new_args[2] = args[1];
        write_inst_string(output, "addiu", new_args, 3);
        return 1;
     } else {
        char* new_args[2];
        new_args[0] = "$at";
        int upper = immediate >> 16;
        char victor[16];
        sprintf(victor, "%d", upper);
        new_args[1] = victor;
        write_inst_string(output, "lui", new_args, 2);
        char* other_args[3];
        other_args[0] = args[0];
        other_args[1] = "$at";
        char ngo[16];
        int16_t lower = immediate & 0xFFFF;
        sprintf(ngo, "%d", lower);
        other_args[2] = ngo;
        write_inst_string(output, "ori", other_args, 3);
        return 2;
      }
    } else if (strcmp(name, "blt") == 0) {
        if (num_args != 3) return 0;
        char* new_args[3];
        new_args[0] = "$at";
        new_args[1] = args[0];
        new_args[2] = args[1];
        write_inst_string(output, "slt", new_args, 3);
        char* other_args[3];
        other_args[0] = "$at";
        other_args[1] = "$0";
        other_args[2] = args[2];
        write_inst_string(output, "bne", other_args, 3);
        return 2;
    } else {
        write_inst_string(output, name, args, num_args);
        return 1;
    }
}  

int write_rtype(uint8_t funct, FILE* output, char** args, size_t num_args) {
    printf("reached");
    if (num_args != 3) return -1;
    printf("reached1");
    int rd = translate_reg(args[0]);
    int rs = translate_reg(args[1]);
    int rt = translate_reg(args[2]);
    if (rs == -1 || rt == -1 || rd == -1) return -1;
    printf("reached2");
    uint32_t instruction =  ((rs << 21) | (rt << 16) | (rd << 11) | funct) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_shift(uint8_t funct, FILE* output, char** args, size_t num_args) {
    if (num_args != 3) return -1;
    long int shamt;
    int rd = translate_reg(args[0]);
    int rt = translate_reg(args[1]);
    int err = translate_num(&shamt, args[2], 0, 31);
    if (rd == -1 || rt == -1 || err == -1 ) return -1;
    uint32_t instruction = ((rt << 16) | (rd << 11) | (shamt << 6) | funct) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_itype(uint8_t opcode, FILE* output, char** args, size_t num_args) {
    if (num_args != 3) return -1;
    int rt = translate_reg(args[0]);
    int rs = translate_reg(args[1]);
    long int immediate;
    int check = translate_num(&immediate, args[2], -32768, 0x7FFF);
    uint16_t negativeShit = immediate | 0x0000;
    if (immediate < 0) immediate = negativeShit;
    if (rt == -1 || rs == -1 || check == -1) return -1; //find bug
    uint32_t instruction =  ((opcode << 26) | (rs << 21) | (rt << 16) | (immediate)) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_jr(uint8_t opcode, FILE* output, char** args, size_t num_args) {
    if (num_args != 1) return -1;
    uint8_t funct = opcode;
    int rs = translate_reg(args[0]);
    if (rs == -1) return -1;
    uint32_t instruction = (rs << 21 | funct) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_branch(uint8_t opcode, FILE* output, char** args, size_t num_args, uint32_t addr, SymbolTable* symtbl) {
    if (num_args != 3) return -1;
    int rs = translate_reg(args[0]);
    int rt = translate_reg(args[1]);
    int64_t address = get_addr_for_symbol(symtbl, args[2]);
    if (rt == -1 || rs == -1 || address == -1) return -1;
    uint16_t offset = (address - addr - 4) >> 2;

    uint32_t instruction =  ((opcode << 26) | (rs << 21) | (rt << 16) | offset) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_jtype(uint8_t opcode, FILE* output, char** args, size_t num_args,uint32_t addr, SymbolTable* reltbl) {
  if (num_args != 1) return -1;
  char* target = args[0];
  int instruction = (opcode << 26) | 0x00000000;
  write_inst_hex(output, instruction);
  if (add_to_table(reltbl, target, addr) == 0) return 0;
  return -1;
}

int write_lui(uint8_t opcode, FILE* output, char** args, size_t num_args) {
    if (num_args != 2) return -1;
    int rt = translate_reg(args[0]);
    long int immediate;
    int check = translate_num(&immediate, args[1], 0, 65535);
    if (rt == -1 || check == -1) return -1;
    uint16_t negativeShit = immediate | 0x0000;
    if (immediate < 0) immediate = negativeShit;
    int instruction = (opcode << 26 | rt << 16 | immediate) | 0x00000000;
    write_inst_hex(output, instruction);
    return 0;
}

int write_mem(uint8_t opcode, FILE* output, char** args, size_t num_args) {
   if (num_args != 3) return -1;
   int rt = translate_reg(args[0]);
   int rs = translate_reg(args[2]);
   long int immediate;
   int check = translate_num(&immediate, args[1], -32768, 0x7FFF);
   if (rt == -1 || rs == -1 || (check == -1 && immediate != 0)) return -1;
   uint16_t negativeShit = immediate | 0x0000;
   if (immediate < 0) immediate = negativeShit;
   int instruction = (opcode << 26 | rs << 21 | rt << 16 | immediate);
   write_inst_hex(output, instruction);
   return 0;
}

int translate_inst(FILE* output, const char* name, char** args, size_t num_args, uint32_t addr,
		   SymbolTable* symtbl, SymbolTable* reltbl) {
    if (strcmp(name, "addu") == 0)       return write_rtype(0x21, output, args, num_args);
    else if (strcmp(name, "or") == 0)    return write_rtype(0x25, output, args, num_args);
    else if (strcmp(name, "slt") == 0)   return write_rtype(0x2a, output, args, num_args);
    else if (strcmp(name, "sltu") == 0)  return write_rtype(0x2b, output, args, num_args);
    else if (strcmp(name, "sll") == 0)   return write_shift(0x00, output, args, num_args);
    else if (strcmp(name, "jr") == 0)    return write_jr(0x08, output, args, num_args);
    else if (strcmp(name, "addiu") == 0) return write_itype(0x09, output, args, num_args);
    else if (strcmp(name, "ori") == 0)   return write_itype(0x0D, output, args, num_args);
    else if (strcmp(name, "lui") == 0)   return write_lui(0x0F, output, args, num_args);
    else if (strcmp(name, "lb") == 0)    return write_mem(0x20, output, args, num_args);
    else if (strcmp(name, "lbu") == 0)   return write_mem(0x24, output, args, num_args);
    else if (strcmp(name, "lw") == 0)    return write_mem(0x23, output, args, num_args);
    else if (strcmp(name, "sb") == 0)    return write_mem(0x28, output, args, num_args);
    else if (strcmp(name, "sw") == 0)    return write_mem(0x2B, output, args, num_args);
    else if (strcmp(name, "beq") == 0)   return write_branch(0x04, output, args, num_args, addr, symtbl);
    else if (strcmp(name, "bne") == 0)   return write_branch(0x05, output, args, num_args, addr, symtbl);
    else if (strcmp(name, "j") == 0)     return write_jtype(0x02, output, args, num_args, addr, reltbl);
    else if (strcmp(name, "jal") == 0)   return write_jtype(0x03, output, args, num_args, addr, reltbl);
    else                                 return -1;
}
