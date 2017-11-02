import unittest
from jsgf import *


class Compilation(unittest.TestCase):
    def test_alt_set(self):
        e1 = AlternativeSet("a")
        e1.tag = "t"
        self.assertEqual(e1.compile(ignore_tags=True), "(a)")
        self.assertEqual(e1.compile(ignore_tags=False), "(a { t })")

        e2 = AlternativeSet("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "(a b)")
        self.assertEqual(e2.compile(ignore_tags=False), "(a b { t })")

        e3 = AlternativeSet("a", "b")
        e3.children[0].tag = "t1"
        e3.children[1].tag = "t2"
        self.assertEqual(e3.compile(ignore_tags=True), "(a|b)")
        self.assertEqual(e3.compile(ignore_tags=False), "(a { t1 }|b { t2 })")

    def test_kleene_star(self):
        e1 = KleeneStar("a")
        e1.tag = "t"
        self.assertEqual(e1.compile(ignore_tags=True), "(a)*")
        self.assertEqual(e1.compile(ignore_tags=False), "(a)* { t }")

        e2 = KleeneStar("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "(a b)*")
        self.assertEqual(e2.compile(ignore_tags=False), "(a b)* { t }")

        e3 = KleeneStar(Sequence("a", "b"))
        e3.tag = "t"
        self.assertEqual(e3.compile(ignore_tags=True), "(a b)*")
        self.assertEqual(e3.compile(ignore_tags=False), "(a b)* { t }")

    def test_literal(self):
        e1 = Literal("a")
        self.assertEqual(e1.compile(ignore_tags=True), "a")

        e2 = Literal("a b")
        self.assertEqual(e2.compile(ignore_tags=True), "a b")

        e3 = Literal("a b")
        e3.tag = "t"
        self.assertEqual(e3.compile(ignore_tags=False), "a b { t }")

    def test_optional_grouping(self):
        e1 = OptionalGrouping("a")
        self.assertEqual(e1.compile(ignore_tags=True), "[a]")

        e2 = OptionalGrouping("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "[a b]")
        self.assertEqual(e2.compile(ignore_tags=False), "[a b] { t }")

    def test_required_grouping(self):
        e1 = RequiredGrouping("a")
        e1.tag = "blah"
        self.assertEqual(e1.compile(ignore_tags=True), "(a)")
        self.assertEqual(e1.compile(ignore_tags=False), "(a { blah })")

        e2 = RequiredGrouping("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "(a b)")
        self.assertEqual(e2.compile(ignore_tags=False), "(a b { t })")

        e3 = RequiredGrouping("a", "b")
        e3.children[0].tag = "t1"
        e3.children[1].tag = "t2"
        self.assertEqual(e3.compile(ignore_tags=True), "(a b)")
        self.assertEqual(e3.compile(ignore_tags=False), "(a { t1 } b { t2 })")

    def test_repeat(self):
        e1 = Repeat("a")
        e1.tag = "t"
        self.assertEqual(e1.compile(ignore_tags=True), "(a)+")
        self.assertEqual(e1.compile(ignore_tags=False), "(a)+ { t }")

        e2 = Repeat("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "(a b)+")
        self.assertEqual(e2.compile(ignore_tags=False), "(a b)+ { t }")

        e3 = Repeat(Sequence("a", "b"))
        e3.tag = "t"
        self.assertEqual(e3.compile(ignore_tags=True), "(a b)+")
        self.assertEqual(e3.compile(ignore_tags=False), "(a b)+ { t }")

    def test_rule_ref(self):
        r = PublicRule("test", "a")
        rule_ref = RuleRef(r)
        rule_ref.tag = "ref"
        self.assertEqual(rule_ref.compile(ignore_tags=True), "<test>")
        self.assertEqual(rule_ref.compile(ignore_tags=False), "<test> { ref }")

    def test_sequence(self):
        e1 = Sequence("a")
        self.assertEqual(e1.compile(ignore_tags=True), "a")

        e2 = Sequence("a b")
        e2.tag = "t"
        self.assertEqual(e2.compile(ignore_tags=True), "a b")
        self.assertEqual(e2.compile(ignore_tags=False), "a b { t }")

        e3 = Sequence("a", "b")
        self.assertEqual(e3.compile(ignore_tags=True), "a b")

        e4 = Sequence("a", "b", "c")
        e4.children[1].tag = "t"
        self.assertEqual(e4.compile(ignore_tags=True), "a b c")
        self.assertEqual(e4.compile(ignore_tags=False), "a b { t } c")


class ParentCase(unittest.TestCase):
    def setUp(self):
        alt_set1 = AlternativeSet("hello", "hi", "hey")
        alt_set2 = AlternativeSet("alice", "bob", "eve")
        self.expansions = [Sequence(alt_set1, alt_set2), alt_set1, alt_set2]

    def test_parent_is_none(self):
        self.assertIsNone(self.expansions[0].parent)

    def check_descendants(self, expansion):
        for child in expansion.children:
            self.assertEqual(expansion, child.parent)
            self.check_descendants(child)

    def test_parent_is_set(self):
        # Recursively test the descendants of the Sequence expansion
        self.check_descendants(self.expansions[0])


class Comparisons(unittest.TestCase):
    def test_literals(self):
        self.assertEqual(Literal("hello"), Literal("hello"))
        self.assertNotEqual(Literal("hey"), Literal("hello"))
        self.assertNotEqual(Literal("hey"), Sequence(Literal("hello")))

    def test_alt_sets(self):
        self.assertEqual(AlternativeSet("hello", "hi"), AlternativeSet("hello", "hi"))
        self.assertNotEqual(AlternativeSet("hello", "hi"), AlternativeSet("hello"))
        self.assertNotEqual(AlternativeSet("hello", "hi"), AlternativeSet("hello"))
        self.assertNotEqual(AlternativeSet("hello", "hi"), Literal("hello"))

    def test_optional(self):
        self.assertEqual(OptionalGrouping("hello"), OptionalGrouping("hello"))
        self.assertNotEqual(OptionalGrouping("hello"), OptionalGrouping("hey"))
        self.assertNotEqual(OptionalGrouping("hello"), AlternativeSet("hello"))

    def test_required_grouping(self):
        self.assertEqual(RequiredGrouping("hello"), RequiredGrouping("hello"))
        self.assertNotEqual(RequiredGrouping("hello"), RequiredGrouping("hey"))
        self.assertNotEqual(RequiredGrouping("hello"), AlternativeSet("hello"))
        self.assertNotEqual(RequiredGrouping("hello"), AlternativeSet("hello"))

    def test_sequence(self):
        self.assertEqual(Sequence("hello"), Sequence("hello"))
        self.assertNotEqual(Sequence("hello"), Sequence("hey"))
        self.assertNotEqual(Sequence("hello"), AlternativeSet("hello"))
        self.assertNotEqual(Sequence("hello"), Literal("hello"))

    def test_repeat(self):
        self.assertEqual(Repeat("hello"), Repeat("hello"))
        self.assertNotEqual(Repeat("hello"), Repeat("hey"))
        self.assertNotEqual(Repeat("hello"), Literal("hello"))
        self.assertNotEqual(Repeat("hello"), Sequence(Literal("hello")))

    def test_kleene_star(self):
        self.assertEqual(KleeneStar("hello"), KleeneStar("hello"))
        self.assertNotEqual(KleeneStar("hello"), KleeneStar("hey"))
        self.assertNotEqual(KleeneStar("hello"), Literal("hello"))
        self.assertNotEqual(KleeneStar("hello"), Sequence(Literal("hello")))

    def test_rule_ref(self):
        rule1 = Rule("test", True, "test")
        rule2 = Rule("test", True, "testing")
        self.assertEqual(RuleRef(rule1), RuleRef(rule1))
        self.assertNotEqual(RuleRef(rule1), RuleRef(rule2))


class AncestorProperties(unittest.TestCase):
    """
    Test the ancestor properties of the Expansion class and its subclasses.
    """
    def test_is_optional(self):
        e1 = OptionalGrouping("hello")
        self.assertTrue(e1.is_optional)

        e2 = Literal("hello")
        self.assertFalse(e2.is_optional)

        e3 = Sequence(Literal("hello"))
        self.assertFalse(e3.is_optional)

        e4 = Sequence(Literal("hello"), OptionalGrouping("there"))
        self.assertFalse(e4.is_optional)
        self.assertTrue(e4.children[1].is_optional)
        self.assertTrue(e4.children[1].child.is_optional)

        e5 = Sequence(
            "a", OptionalGrouping("b"),
            Sequence("c", OptionalGrouping("d"))
        )

        a = e5.children[0]
        opt1 = e5.children[1]
        b = opt1.child
        seq2 = e5.children[2]
        c = seq2.children[0]
        opt2 = seq2.children[1]
        d = opt2.child
        self.assertFalse(e5.is_optional)
        self.assertFalse(a.is_optional)
        self.assertTrue(opt1.is_optional)
        self.assertTrue(opt2.is_optional)
        self.assertTrue(b.is_optional)
        self.assertTrue(opt2.is_optional)
        self.assertTrue(d.is_optional)
        self.assertFalse(c.is_optional)

    def test_is_alternative(self):
        e1 = AlternativeSet("hello")
        self.assertTrue(e1.is_alternative)

        e2 = Literal("hello")
        self.assertFalse(e2.is_alternative)

        e3 = Sequence(Literal("hello"))
        self.assertFalse(e3.is_alternative)

        e4 = AlternativeSet(Literal("hello"), Literal("hi"), Literal("hey"))
        for child in e4.children:
            self.assertTrue(child.is_alternative)

        e5 = Sequence(e4)
        self.assertFalse(e5.is_alternative)

        e6 = AlternativeSet(Literal("hello"), AlternativeSet("hi there",
                                                             "hello there"),
                            Literal("hey"))
        for leaf in e6.leaves:
            self.assertTrue(leaf.is_alternative)


class LiteralRepetitionAncestor(unittest.TestCase):
    def setUp(self):
        self.seq = Sequence("hello", "world")

    def test_no_repetition(self):
        self.assertIsNone(Literal("hello").repetition_ancestor)
        self.assertFalse(self.seq.children[0].repetition_ancestor)
        self.assertFalse(self.seq.children[1].repetition_ancestor)

    def test_with_repeat(self):
        rep1 = Repeat("hello")
        rep2 = Repeat(self.seq)
        self.assertEqual(rep1.child.repetition_ancestor, rep1)
        self.assertEqual(rep2.child.children[0].repetition_ancestor, rep2)

    def test_with_kleene_star(self):
        k1 = KleeneStar("hello")
        k2 = KleeneStar(self.seq)
        self.assertEqual(k1.child.repetition_ancestor, k1)
        self.assertEqual(k2.child.children[1].repetition_ancestor, k2)


class MutuallyExclusiveOfCase(unittest.TestCase):
    def test_no_alternative_sets(self):
        e1 = Literal("hi")
        e2 = Literal("hello")
        self.assertFalse(e1.mutually_exclusive_of(e2))

    def test_one_alternative_set(self):
        e1 = AlternativeSet("hi", "hello")
        self.assertTrue(e1.children[0].mutually_exclusive_of(e1.children[1]))

        e2 = AlternativeSet(Sequence("hi", "there"), "hello")
        self.assertTrue(e2.children[0]
                        .mutually_exclusive_of(e2.children[1]))
        self.assertTrue(e2.children[0].children[0]
                        .mutually_exclusive_of(e2.children[1]))
        self.assertTrue(e2.children[0].children[1]
                        .mutually_exclusive_of(e2.children[1]))

    def test_two_alternative_sets(self):
        e1 = Sequence(AlternativeSet(Sequence("a", "b"), "c"),
                      AlternativeSet("d", "e"))
        as1, as2 = e1.children[0], e1.children[1]
        seq2 = as1.children[0]
        a, b, c = seq2.children[0], seq2.children[1], as1.children[1]
        d, e = as2.children[0], as2.children[1]

        self.assertFalse(as1.mutually_exclusive_of(as2))
        self.assertTrue(a.mutually_exclusive_of(c))
        self.assertTrue(b.mutually_exclusive_of(c))
        self.assertFalse(a.mutually_exclusive_of(b))

        self.assertTrue(d.mutually_exclusive_of(e) and e.mutually_exclusive_of(d),
                        "mutual exclusivity should be an associative operation")
        self.assertFalse(a.mutually_exclusive_of(d))
        self.assertFalse(a.mutually_exclusive_of(e))


class MapExpansionCase(unittest.TestCase):
    """
    Test the map_expansion function.
    """
    def setUp(self):
        self.map_to_string = lambda x: "%s" % x
        self.map_to_current_match = lambda x: x.current_match

    def test_base(self):
        e = Literal("hello")
        mapped = map_expansion(e, self.map_to_string)
        self.assertEqual(mapped[0], "%s" % e)

    def test_simple(self):
        e = Sequence("hello", "world")
        mapped = map_expansion(e, self.map_to_string)
        self.assertEqual(mapped, (
            "Sequence(Literal('hello'), Literal('world'))", (
                ("Literal('hello')", ()),
                ("Literal('world')", ())
            )))

    def test_with_matches(self):
        e = Sequence("hello", "world")
        e.matches("hello world")  # assuming matches tests pass
        mapped = map_expansion(e, self.map_to_current_match)
        self.assertEqual(mapped, (
            "hello world", (
                ("hello", ()),
                ("world", ())
            )))


class LeavesProperty(unittest.TestCase):
    """
    Test the leaves property of the Expansion classes.
    """
    def test_base(self):
        e = Literal("hello")
        self.assertListEqual(e.leaves, [Literal("hello")])

    def test_new_leaf_type(self):
        class TestLeaf(Expansion):
            def __init__(self):
                super(TestLeaf, self).__init__([])

        e = TestLeaf()
        self.assertListEqual(e.leaves, [TestLeaf()])

    def test_multiple(self):
        e = Sequence(Literal("hello"), AlternativeSet("there", "friend"))
        self.assertListEqual(e.leaves, [Literal("hello"), Literal("there"),
                                        Literal("friend")],
                             "leaves should be in sequence from left to right.")

    def test_with_rule_ref(self):
        r = PublicRule("test", Literal("hi"))
        e = RuleRef(r)
        self.assertListEqual(e.leaves, [Literal("hi")])


class RootExpansionProperty(unittest.TestCase):
    def test_base(self):
        e = Literal("hello")
        self.assertEqual(e.root_expansion, e)

    def test_multiple(self):
        e = Sequence(Literal("hello"), AlternativeSet("there", "friend"))
        hello = e.children[0]
        alt_set = e.children[1]
        there = e.children[1].children[0]
        friend = e.children[1].children[1]
        self.assertEqual(e.root_expansion, e)
        self.assertEqual(alt_set.root_expansion, e)
        self.assertEqual(hello.root_expansion, e)
        self.assertEqual(there.root_expansion, e)
        self.assertEqual(friend.root_expansion, e)


if __name__ == '__main__':
    unittest.main()
