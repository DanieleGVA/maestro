/**
 * QuizView -- quiz interface component (F11.8).
 *
 * Displays one question at a time with multiple-choice options.
 * No timer (accessibility spec Section 2.1, WCAG 2.2.1).
 * Feedback after each answer with aria-live="assertive".
 * Tone is always encouraging (safeguarding).
 *
 * Options use radio group pattern (accessibility spec Section 6.4).
 */

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  AccessibilityInfo,
} from 'react-native';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../theme/typography';
import { FOCUS_RING } from '../theme/tokens';
import type { QuizQuestion, QuizOption, QuestionFeedback } from '../types';

interface QuizViewProps {
  questions: QuizQuestion[];
  onSubmitAll: (answers: Record<string, string>) => void;
  feedback: QuestionFeedback[] | null;
}

export default function QuizView({ questions, onSubmitAll, feedback }: QuizViewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showFeedback, setShowFeedback] = useState(false);

  const question = questions[currentIndex];
  const selectedOption = answers[question?.id];
  const isLastQuestion = currentIndex === questions.length - 1;
  const allAnswered = questions.every((q) => answers[q.id]);
  const currentFeedback = feedback?.find((f) => f.questionId === question?.id);

  const selectOption = (optionId: string) => {
    setAnswers((prev) => ({ ...prev, [question.id]: optionId }));
  };

  const goNext = () => {
    if (isLastQuestion && allAnswered) {
      onSubmitAll(answers);
      setShowFeedback(true);
    } else if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const goPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (!question) return null;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      {/* Progress indicator */}
      <View
        accessible
        accessibilityRole="text"
        accessibilityLabel={`Domanda ${currentIndex + 1} di ${questions.length}`}
      >
        <Text style={styles.progress}>
          Domanda {currentIndex + 1} di {questions.length}
        </Text>
      </View>

      {/* Progress bar */}
      <View
        accessible
        accessibilityRole="progressbar"
        accessibilityLabel={`Progresso quiz: ${currentIndex + 1} di ${questions.length} domande`}
        accessibilityValue={{
          min: 0,
          max: questions.length,
          now: currentIndex + 1,
        }}
        style={styles.progressTrack}
      >
        <View
          style={[
            styles.progressFill,
            { width: `${((currentIndex + 1) / questions.length) * 100}%` },
          ]}
        />
      </View>

      {/* Question text */}
      <Text
        style={styles.questionText}
        accessible
        accessibilityRole="header"
      >
        {question.text}
      </Text>

      {/* Code block (if present) */}
      {question.codeBlock && (
        <View style={styles.codeBlock} accessible accessibilityLabel={`Codice: ${question.codeBlock}`}>
          <Text style={styles.codeText}>{question.codeBlock}</Text>
        </View>
      )}

      {/* Options (radio group pattern) */}
      <View
        accessibilityRole="radiogroup"
        accessibilityLabel={`Opzioni per: ${question.text}`}
      >
        {question.options.map((option, index) => {
          const isSelected = selectedOption === option.id;
          const letter = String.fromCharCode(65 + index); // A, B, C, D

          return (
            <TouchableOpacity
              key={option.id}
              accessible
              accessibilityRole="radio"
              accessibilityLabel={`Opzione ${letter}: ${option.text}`}
              accessibilityState={{ checked: isSelected }}
              style={[
                styles.option,
                isSelected && styles.optionSelected,
              ]}
              onPress={() => selectOption(option.id)}
              activeOpacity={0.7}
            >
              <View style={[styles.radio, isSelected && styles.radioSelected]}>
                {isSelected && <View style={styles.radioInner} />}
              </View>
              <View style={styles.optionContent}>
                <Text style={styles.optionLetter}>{letter}.</Text>
                <Text style={styles.optionText}>{option.text}</Text>
              </View>
              {option.codeBlock && (
                <View style={styles.optionCode}>
                  <Text style={styles.codeText}>{option.codeBlock}</Text>
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Feedback (after submission) */}
      {showFeedback && currentFeedback && (
        <View
          accessible
          accessibilityRole="alert"
          accessibilityLiveRegion="assertive"
          style={[
            styles.feedback,
            currentFeedback.correct ? styles.feedbackCorrect : styles.feedbackIncorrect,
          ]}
        >
          <Text style={styles.feedbackTitle}>
            {currentFeedback.correct ? 'Risposta corretta' : 'Risposta errata'}
          </Text>
          <Text style={styles.feedbackText}>{currentFeedback.explanation}</Text>
        </View>
      )}

      {/* Navigation buttons */}
      <View style={styles.buttons}>
        {currentIndex > 0 && (
          <TouchableOpacity
            accessible
            accessibilityRole="button"
            accessibilityLabel="Domanda precedente"
            style={styles.buttonSecondary}
            onPress={goPrev}
          >
            <Text style={styles.buttonSecondaryText}>Precedente</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          accessible
          accessibilityRole="button"
          accessibilityLabel={
            isLastQuestion && allAnswered
              ? 'Conferma tutte le risposte'
              : selectedOption
                ? 'Vai alla domanda successiva'
                : 'Seleziona una risposta per procedere'
          }
          accessibilityState={{ disabled: !selectedOption }}
          style={[styles.buttonPrimary, !selectedOption && styles.buttonDisabled]}
          onPress={goNext}
          disabled={!selectedOption}
        >
          <Text style={styles.buttonPrimaryText}>
            {isLastQuestion && allAnswered ? 'Conferma' : 'Successiva'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: PAGE_COLORS.bg,
  },
  content: {
    padding: SPACING.lg,
  },
  progress: {
    fontSize: TEXT_SIZES.sm,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginBottom: SPACING.sm,
  },
  progressTrack: {
    height: 6,
    backgroundColor: '#E0E0E0',
    borderRadius: 3,
    marginBottom: SPACING.xl,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#1565C0',
    borderRadius: 3,
  },
  questionText: {
    fontSize: TEXT_SIZES.lg,
    lineHeight: TEXT_SIZES.lg * LINE_HEIGHTS.normal,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.lg,
  },
  codeBlock: {
    backgroundColor: '#F5F5F5',
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.md,
    marginBottom: SPACING.lg,
    borderLeftWidth: 3,
    borderLeftColor: PAGE_COLORS.borderInput,
  },
  codeText: {
    fontFamily: 'monospace',
    fontSize: TEXT_SIZES.sm,
    lineHeight: TEXT_SIZES.sm * LINE_HEIGHTS.relaxed,
    color: PAGE_COLORS.fg,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: SPACING.md,
    marginBottom: SPACING.sm,
    borderWidth: 1.5,
    borderColor: PAGE_COLORS.borderInput,
    borderRadius: BORDER_RADIUS.md,
    minHeight: TOUCH_TARGET.min,
    backgroundColor: PAGE_COLORS.bg,
  },
  optionSelected: {
    borderColor: FOCUS_RING.color,
    backgroundColor: '#E3F2FD',
  },
  radio: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: PAGE_COLORS.borderInput,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
    marginTop: 2,
  },
  radioSelected: {
    borderColor: FOCUS_RING.color,
  },
  radioInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: FOCUS_RING.color,
  },
  optionContent: {
    flex: 1,
    flexDirection: 'row',
    gap: SPACING.xs,
  },
  optionLetter: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  optionText: {
    flex: 1,
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  optionCode: {
    marginTop: SPACING.sm,
    backgroundColor: '#F5F5F5',
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.sm,
    marginLeft: 36,
  },
  feedback: {
    padding: SPACING.lg,
    borderRadius: BORDER_RADIUS.md,
    marginTop: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  feedbackCorrect: {
    backgroundColor: '#E8F5E9',
    borderLeftWidth: 4,
    borderLeftColor: '#2E7D32',
  },
  feedbackIncorrect: {
    backgroundColor: '#FFF3E0',
    borderLeftWidth: 4,
    borderLeftColor: '#EF6C00',
  },
  feedbackTitle: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xs,
  },
  feedbackText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: SPACING.xl,
    gap: SPACING.md,
  },
  buttonPrimary: {
    flex: 1,
    backgroundColor: '#1565C0',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  buttonSecondary: {
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: PAGE_COLORS.borderInput,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonPrimaryText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
  buttonSecondaryText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
});
