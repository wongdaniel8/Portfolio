#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <CUnit/Basic.h>
#include "src/utils.h"
#include "src/tables.h"
#include "src/translate_utils.h"
#include "src/translate.h"
const char* TMP_FILE = "test_output.txt";
const int BUF_SIZE = 1024;
/****************************************
 *  Helper functions
 ****************************************/
int do_nothing() {
    return 0;
}
int init_log_file() {
    set_log_file(TMP_FILE);
    return 0;
}
int check_lines_equal(char **arr, int num) {
    char buf[BUF_SIZE];
    FILE *f = fopen(TMP_FILE, "r");
    if (!f) {
	CU_FAIL("Could not open temporary file");
	return 0;
    }
    for (int i = 0; i < num; i++) {
	if (!fgets(buf, BUF_SIZE, f)) {
	    CU_FAIL("Reached end of file");
	    return 0;
	}
	CU_ASSERT(!strncmp(buf, arr[i], strlen(arr[i])));
    }
    fclose(f);
    return 0;
}
/****************************************
 *  Test cases for translate_utils.c
 ****************************************/
void test_translate_reg() {
    CU_ASSERT_EQUAL(translate_reg("$0"), 0);
    CU_ASSERT_EQUAL(translate_reg("$at"), 1);
    CU_ASSERT_EQUAL(translate_reg("$v0"), 2);
    CU_ASSERT_EQUAL(translate_reg("$a0"), 4);
    CU_ASSERT_EQUAL(translate_reg("$a1"), 5);
    CU_ASSERT_EQUAL(translate_reg("$a2"), 6);
    CU_ASSERT_EQUAL(translate_reg("$a3"), 7);
    CU_ASSERT_EQUAL(translate_reg("$t0"), 8);
    CU_ASSERT_EQUAL(translate_reg("$t1"), 9);
    CU_ASSERT_EQUAL(translate_reg("$t2"), 10);
    CU_ASSERT_EQUAL(translate_reg("$t3"), 11);
    CU_ASSERT_EQUAL(translate_reg("$s0"), 16);
    CU_ASSERT_EQUAL(translate_reg("$s1"), 17);
    CU_ASSERT_EQUAL(translate_reg("$3"), -1);
    CU_ASSERT_EQUAL(translate_reg("asdf"), -1);
    CU_ASSERT_EQUAL(translate_reg("hey there"), -1);
}
void test_translate_num() {
    long int output;
    CU_ASSERT_EQUAL(translate_num(&output, "35", -1000, 1000), 0);
    CU_ASSERT_EQUAL(output, 35);
    CU_ASSERT_EQUAL(translate_num(&output, "145634236", 0, 9000000000), 0);
    CU_ASSERT_EQUAL(output, 145634236);
    CU_ASSERT_EQUAL(translate_num(&output, "0xC0FFEE", -9000000000, 9000000000), 0);
    CU_ASSERT_EQUAL(output, 12648430);
    CU_ASSERT_EQUAL(translate_num(&output, "72", -16, 72), 0);
    CU_ASSERT_EQUAL(output, 72);
    CU_ASSERT_EQUAL(translate_num(&output, "72", -16, 71), -1);
    CU_ASSERT_EQUAL(translate_num(&output, "72", 72, 150), 0);
    CU_ASSERT_EQUAL(output, 72);
    CU_ASSERT_EQUAL(translate_num(&output, "72", 73, 150), -1);
    CU_ASSERT_EQUAL(translate_num(&output, "35x", -100, 100), -1);
}
/****************************************
 *  Test cases for tables.c
 ****************************************/
void test_table_1() {
    int retval;
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    CU_ASSERT_PTR_NOT_NULL(tbl);
    retval = add_to_table(tbl, "abc", 8);
    CU_ASSERT_EQUAL(retval, 0);
    retval = add_to_table(tbl, "efg", 12);
    CU_ASSERT_EQUAL(retval, 0);
    retval = add_to_table(tbl, "q45", 16);
    CU_ASSERT_EQUAL(retval, 0);
    retval = add_to_table(tbl, "q45", 24);
    CU_ASSERT_EQUAL(retval, -1);
    retval = add_to_table(tbl, "bob", 14);
    CU_ASSERT_EQUAL(retval, -1);
    retval = get_addr_for_symbol(tbl, "abc");
    CU_ASSERT_EQUAL(retval, 8);
    retval = get_addr_for_symbol(tbl, "q45");
    CU_ASSERT_EQUAL(retval, 16);
    retval = get_addr_for_symbol(tbl, "ef");
    CU_ASSERT_EQUAL(retval, -1);
    free_table(tbl);
    char* arr[] = { "Error: name 'q45' already exists in table.",
		    "Error: address is not a multiple of 4." };
    check_lines_equal(arr, 2);
    SymbolTable* tbl2 = create_table(SYMTBL_NON_UNIQUE);
    CU_ASSERT_PTR_NOT_NULL(tbl2);
    retval = add_to_table(tbl, "q45", 16);
    CU_ASSERT_EQUAL(retval, 0);
    retval = add_to_table(tbl, "q45", 24);
    CU_ASSERT_EQUAL(retval, 0);
    free_table(tbl2);
}

void test_table_2() {
    int retval, max = 100;
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    CU_ASSERT_PTR_NOT_NULL(tbl);
    char buf[10];
    for (int i = 0; i < max; i++) {
	sprintf(buf, "%d", i);
	retval = add_to_table(tbl, buf, 4 * i);
	CU_ASSERT_EQUAL(retval, 0);
    }
    for (int i = 0; i < max; i++) {
	sprintf(buf, "%d", i);
	retval = get_addr_for_symbol(tbl, buf);
	CU_ASSERT_EQUAL(retval, 4 * i);
    }
    free_table(tbl);
}
/****************************************/

void test_translate_rtype() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    char* args[3];
    args[0] = "$t0";
    args[1] = "$t1";
    args[2] = "$t2";
    int check = translate_inst(tester, "addu", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, 0);
    args[2] = "$dragon";
    int check2 = translate_inst(tester, "addu", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, -1);
    args[2] = NULL;
    int check3 = translate_inst(tester, "addu", args, 2, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    free(tbl);
    free(tbl2);
}

void test_translate_itype() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    char* args[3];
    args[0] = "$t0";
    args[1] = "$t1";
    args[2] = "$t2";
    int check = translate_inst(tester, "addiu", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, -1);
    args[2] = "1000";
    int check2 = translate_inst(tester, "addiu", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, 0);
    args[2]= "111111111111111111111111111111111111111111111111111111111111111111111111";
    int check3 = translate_inst(tester, "addiu", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    free(tbl);
    free(tbl2);
}

void test_translate_jtype() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    add_to_table(tbl2,"dragon", 0x00000010);
    char* args[1];
    args[0] = "dragon";
    int check = translate_inst(tester, "jal", args, 1, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, 0);
    args[0] = "leprechaun";
    int check2 = translate_inst(tester, "jal", args, 1, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, -1);
    int check3 = translate_inst(tester, "jal", args, 2, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    free(tbl);
    free(tbl2);
}

void test_translate_shift() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    char* args[3];
    args[0] = "$t0";
    args[1] = "$t1";
    args[2] = "$t2";
    int check = translate_inst(tester, "sll", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, -1);
    args[2] = "5";
    int check2 = translate_inst(tester, "sll", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, 0);
    args[2] = "-5";
    int check3 = translate_inst(tester, "sll", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    args[2] = "1000";
    int check4 = translate_inst(tester, "sll", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check4, -1);
    free(tbl);
    free(tbl2);
}

void test_translate_branch() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    add_to_table(tbl,"ninja", 0x00000100);
    char* args[3];
    args[0] = "$t0";
    args[1] = "$t1";
    args[2] = "ninja";
    int check = translate_inst(tester, "beq", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, 0);
    args[2] = "sneevil";
    int check2 = translate_inst(tester, "beq", args, 3, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, -1);
    int check3 = translate_inst(tester, "beq", args, 2, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    free(tbl);
    free(tbl2);
}

void test_translate_jr() {
    FILE* tester = fopen("test.txt", "w");
    SymbolTable* tbl = create_table(SYMTBL_UNIQUE_NAME);
    SymbolTable* tbl2 = create_table(SYMTBL_UNIQUE_NAME);
    char* args[1];
    args[0] = "1000";
    int check = translate_inst(tester, "jr", args, 1, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check, -1);
    args[0] = "$ra";
    int check2 = translate_inst(tester, "jr", args, 1, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check2, 0);
    int check3 = translate_inst(tester, "jr", args, 2, 0, tbl, tbl2);
    CU_ASSERT_EQUAL(check3, -1);
    free(tbl);
    free(tbl2);
}

void test_write_pass_one() {
    char name[] = "li";
    char *args[2] = {"$t1", "0x02"};
    CU_ASSERT_EQUAL(write_pass_one(TMP_FILE, name, args, 2), 1);
    char *args2[2] = {"$t1", "0x22222222"};
    CU_ASSERT_EQUAL(write_pass_one(TMP_FILE, name, args2, 2), 2);
    char bne[] = "blt";
    char *args3[3] = {"$t1", "$t2", "label1"};
    CU_ASSERT_EQUAL(write_pass_one(TMP_FILE, bne, args3, 3), 2);
    char *args4[3] = {"$t1", "$t2","t3", "label1"};
    CU_ASSERT_EQUAL(write_pass_one(TMP_FILE, bne, args4, 4), 0);
    char *args5[2] = {"$t1", "0x2222222222222222222222222222222"};
    CU_ASSERT_EQUAL(write_pass_one(TMP_FILE, name, args5, 2), 0);
}
/****************************************/
int main(int argc, char** argv) {
    CU_pSuite pSuite1 = NULL, pSuite2 = NULL, pSuite3 = NULL, pSuite4 = NULL;
    if (CUE_SUCCESS != CU_initialize_registry()) {
	return CU_get_error();
    }
    /* Suite 1 */
    pSuite1 = CU_add_suite("Testing translate_utils.c", NULL, NULL);
    if (!pSuite1) {
	goto exit;
    }
    if (!CU_add_test(pSuite1, "test_translate_reg", test_translate_reg)) {
	goto exit;
    }
    if (!CU_add_test(pSuite1, "test_translate_num", test_translate_num)) {
	goto exit;
    }
    /* Suite 2 */
    pSuite2 = CU_add_suite("Testing tables.c", init_log_file, NULL);
    if (!pSuite2) {
	goto exit;
    }
    if (!CU_add_test(pSuite2, "test_table_1", test_table_1)) {
	goto exit;
    }
    if (!CU_add_test(pSuite2, "test_table_2", test_table_2)) {
	goto exit;
    }
    /* Suite 3 */
    pSuite3 = CU_add_suite("Testing translate.c", NULL, NULL);
    if (!pSuite3) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_rtype", test_translate_rtype)) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_itype", test_translate_itype)) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_jtype", test_translate_jtype)) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_shift", test_translate_shift)) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_jr", test_translate_jr)) {
	goto exit;
    }
    if (!CU_add_test(pSuite3, "test_translate_branch", test_translate_branch)) {
	goto exit;
    }
    pSuite4 = CU_add_suite("Testing write_pass_one", NULL, NULL);
    if (!pSuite4) {
	goto exit;
    }
    if (!CU_add_test(pSuite4, "test_write_pass_one", test_write_pass_one)) {
	goto exit;
    }
    CU_basic_set_mode(CU_BRM_VERBOSE);
    CU_basic_run_tests();
 exit:
    CU_cleanup_registry();
    return CU_get_error();;
}
