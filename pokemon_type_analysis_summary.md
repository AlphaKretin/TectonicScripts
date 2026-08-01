# Statistical Analysis Summary: Which Types Learn Which Types of Moves?

A summary of the analytical pipeline from [Alish's video](https://www.youtube.com/watch?v=A6cMC7RvF-8), for replication on a different dataset.

---

## Dataset Specification

- **Source:** Veekun's Pokémon database
- **Scope:** Generations 6–8 (post-Fairy-type introduction)
- **Move learning methods included:** level-up, breeding, TM, HM, TR, tutoring
- **Move filter:** Damage-dealing attacks only (no status moves)
- **Secondary pass:** All analyses repeated on "natural" moves only (level-up + egg moves) for comparison

---

## Analysis 1: Move Type Learnability

**Question:** How widely distributed is each move type across Pokémon?

**Method:**
- For each move type `T`, consider only Pokémon that are **not** of type `T`
- Calculate the **percentage** of those Pokémon that can learn at least one damaging move of type `T`
- The cross-type filter prevents a type's own Pokémon from inflating its learnability score

**Output:** A ranked list of all 18 types by learnability percentage.

**Repeat** with natural-only movesets to produce a separate learnability ranking.

---

## Analysis 2: Per-Type Move-Learning Affinity Matrix

**Question:** For each Pokémon type, how likely are its members to learn moves of each other type?

**Method:**
- Build an 18×18 matrix where each cell `[PokémonType, MoveType]` = percentage of Pokémon of that type (excluding those that are also of `MoveType`) who can learn at least one move of `MoveType`
- The Normal move column can be omitted as it is near-universal and not informative

**Output:** A matrix/heatmap of cross-type learning rates.

---

## Analysis 3: Type Versatility Score (Weighted Affinity) ⭐

**Question:** Which Pokémon type is most versatile — i.e. learns the broadest spread of move types, adjusted for how rare those move types are?

**Method (per Pokémon type `T`):**

1. For each move type `M` (where `M ≠ T`):
   - `P_in` = % of type-`T` Pokémon that can learn a move of type `M`
   - `P_out` = % of non-type-`T` Pokémon that can learn a move of type `M` (from Analysis 1)
   - **Affinity** = `P_in − P_out`

2. Compute a **weighted average** of all affinities across move types, where the weight for move type `M` = **inverse of `M`'s learnability score** (from Analysis 1)
   - Rationale: learning a rarely-distributed move type should count for more than learning a commonly-distributed one

3. This weighted average is the **versatility score** for type `T`

**Output:** A ranked list of all 18 Pokémon types by versatility score.

**Repeat** with natural-only movesets.

---

## Analysis 4: Dual-Type Confound Check

**Question:** Does dual-typing distort the versatility scores (e.g. do Flying types appear versatile only because they are commonly paired with Normal)?

**Method:**
- Identify the most common dual-type combinations (e.g. Normal/Flying, Grass/Poison, Bug/Poison, Bug/Flying)
- For each candidate confound, check whether the secondary type is **necessary** to explain cross-type move access
  - e.g. Do Normal/Flying Pokémon account for all Flying-type Ice or Electric move access?
- General check: for any move type `Z` learned by a Pokémon of type `X`, determine whether those Pokémon required being dual-type `Y` to access it

**Output:** A qualitative conclusion on whether dual-type correction is needed. (In the original analysis, only two edge-case Pokémon required exclusion; the effect was deemed negligible.)

---

## Analysis 5: Versatility vs. Learnability Scatterplot

**Question:** Is there a systematic relationship between a type's versatility score and its learnability?

**Method:**
- Plot each type as a point: versatility score (one axis) vs. learnability percentage (other axis)
- Visually assess for correlation or clustering

**Output:** A scatterplot. Expect a rough "specialist–generalist" axis, where types that are widely learnable also tend to have high versatility scores, with some outliers.

---

## Analysis 6: Full-Coverage Individual Pokémon

**Question:** Which individual Pokémon can learn at least one damaging move of every type?

**Method:**
- For each Pokémon, take the union of all learnable damaging moves across their full learnset
- Check whether that union contains at least one move of each of the 18 types
- Separately identify Pokémon with 17/18 type coverage

**Output:** A list of Pokémon with full or near-full type coverage in their learnset.

---

## Notes for Replication

- The core novel contribution is **Analysis 3**: the inverse-learnability-weighted affinity score. Analyses 1 and 2 are prerequisites that feed into it.
- The "natural moves only" secondary pass requires filtering the learnset to level-up and egg moves before running all analyses from scratch.
- Dual-typing complicates the affinity calculation slightly — a Pokémon of type `X/Y` should be excluded from both the type-`X` "in" group and the type-`Y` "in" group when calculating affinity for those respective types.
