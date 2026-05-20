/**
 * Quiz screen (SCR-ST-07).
 *
 * Displays quiz questions one at a time with multiple-choice options.
 * No timer (WCAG 2.2.1, accessibility spec).
 * Feedback after submission with encouraging tone.
 * Result screen shows state transition if applicable.
 *
 * Heading: h1 = "Quiz: {concetto}" (accessibility spec Section 7.3).
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  StyleSheet,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import QuizView from '../../components/QuizView';
import StateIndicator from '../../components/StateIndicator';
import { useQuiz } from '../../hooks/useApi';
import { SPACING, BORDER_RADIUS, TOUCH_TARGET, PAGE_COLORS } from '../../theme/spacing';
import { TEXT_SIZES, LINE_HEIGHTS } from '../../theme/typography';
import type { QuestionFeedback, MasteryState } from '../../types';

export default function QuizScreen() {
  const { quizId } = useLocalSearchParams<{ quizId: string }>();
  const router = useRouter();
  const {
    quiz,
    quizLoading,
    quizError,
    result,
    resultLoading,
    resultError,
    submit,
  } = useQuiz();

  const [feedback, setFeedback] = useState<QuestionFeedback[] | null>(null);
  const [startTime] = useState(Date.now());

  const handleSubmitAll = async (answers: Record<string, string>) => {
    if (!quizId) return;

    const answerList = Object.entries(answers).map(([question_id, selected]) => ({
      question_id,
      selected,
    }));
    const totalTimeMs = Date.now() - startTime;
    const quizResult = await submit(quizId, answerList, totalTimeMs);

    if (quizResult?.perQuestion) {
      setFeedback(quizResult.perQuestion);
    }
  };

  // Loading state
  if (quizLoading) {
    return (
      <View style={styles.center} accessible accessibilityLabel="Caricamento quiz in corso">
        <ActivityIndicator size="large" color="#1565C0" />
        <Text style={styles.loadingText}>Preparazione del quiz...</Text>
      </View>
    );
  }

  // Error state
  if (quizError) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText} accessible accessibilityRole="alert">
          {quizError}
        </Text>
        <TouchableOpacity
          accessible
          accessibilityRole="button"
          accessibilityLabel="Torna indietro"
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Text style={styles.backText}>Torna indietro</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Result screen
  if (result) {
    const isPass = result.score >= 80;
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.resultContent}>
        <Text style={styles.resultTitle} accessible accessibilityRole="header">
          Risultato
        </Text>

        {/* Score */}
        <View
          style={[styles.scoreCard, isPass ? styles.scorePass : styles.scoreRetry]}
          accessible
          accessibilityRole="alert"
          accessibilityLiveRegion="assertive"
          accessibilityLabel={`Punteggio: ${result.score} percento. ${result.correctCount} risposte corrette su ${result.totalQuestions}`}
        >
          <Text style={styles.scoreNumber}>{result.score}%</Text>
          <Text style={styles.scoreDetail}>
            {result.correctCount}/{result.totalQuestions} risposte corrette
          </Text>
        </View>

        {/* Feedback message (encouraging) */}
        <Text style={styles.feedbackMessage}>{result.feedbackMessage}</Text>

        {/* State transition */}
        {result.transitionTriggered && (
          <View style={styles.transitionCard}>
            <Text style={styles.transitionTitle}>Aggiornamento stato</Text>
            <Text style={styles.transitionText}>
              {result.transitionTriggered === 'quiz_superato'
                ? 'Il tuo stato e\' stato aggiornato. Complimenti!'
                : 'Nessun problema, puoi riprovare con un approccio diverso.'}
            </Text>
          </View>
        )}

        {/* Actions */}
        <TouchableOpacity
          accessible
          accessibilityRole="button"
          accessibilityLabel="Torna alla mappa"
          style={styles.primaryButton}
          onPress={() => router.replace('/map')}
          activeOpacity={0.7}
        >
          <Text style={styles.primaryButtonText}>Torna alla mappa</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  // Quiz in progress (placeholder for when quiz generation is wired up)
  if (quiz?.questions && quiz.questions.length > 0) {
    return (
      <QuizView
        questions={quiz.questions}
        onSubmitAll={handleSubmitAll}
        feedback={feedback}
      />
    );
  }

  // Fallback: no quiz data
  return (
    <View style={styles.center}>
      <Text style={styles.loadingText}>
        Il quiz sara' disponibile a breve.
      </Text>
      <TouchableOpacity
        accessible
        accessibilityRole="button"
        accessibilityLabel="Torna indietro"
        style={styles.backButton}
        onPress={() => router.back()}
      >
        <Text style={styles.backText}>Torna indietro</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: PAGE_COLORS.bg,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: PAGE_COLORS.bg,
    padding: SPACING.xl,
  },
  loadingText: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginTop: SPACING.md,
    textAlign: 'center',
  },
  errorText: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    textAlign: 'center',
    marginBottom: SPACING.lg,
  },
  backButton: {
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
    paddingVertical: SPACING.sm,
  },
  backText: {
    fontSize: TEXT_SIZES.sm,
    color: '#1565C0',
    fontFamily: 'Inter',
    fontWeight: '500',
  },
  resultContent: {
    padding: SPACING.lg,
  },
  resultTitle: {
    fontSize: TEXT_SIZES['2xl'],
    lineHeight: TEXT_SIZES['2xl'] * LINE_HEIGHTS.tight,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  scoreCard: {
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.xl,
    alignItems: 'center',
    marginBottom: SPACING.lg,
  },
  scorePass: {
    backgroundColor: '#E8F5E9',
    borderWidth: 2,
    borderColor: '#2E7D32',
  },
  scoreRetry: {
    backgroundColor: '#FFF3E0',
    borderWidth: 2,
    borderColor: '#EF6C00',
  },
  scoreNumber: {
    fontSize: 48,
    fontWeight: '700',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
  },
  scoreDetail: {
    fontSize: TEXT_SIZES.base,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
    marginTop: SPACING.xs,
  },
  feedbackMessage: {
    fontSize: TEXT_SIZES.lg,
    lineHeight: TEXT_SIZES.lg * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    textAlign: 'center',
    marginBottom: SPACING.xl,
  },
  transitionCard: {
    backgroundColor: PAGE_COLORS.surfaceBg,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.lg,
    marginBottom: SPACING.xl,
  },
  transitionTitle: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: PAGE_COLORS.fg,
    fontFamily: 'Inter',
    marginBottom: SPACING.xs,
  },
  transitionText: {
    fontSize: TEXT_SIZES.base,
    lineHeight: TEXT_SIZES.base * LINE_HEIGHTS.normal,
    color: PAGE_COLORS.surfaceFg,
    fontFamily: 'Inter',
  },
  primaryButton: {
    backgroundColor: '#1565C0',
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    minHeight: TOUCH_TARGET.min,
    justifyContent: 'center',
  },
  primaryButtonText: {
    fontSize: TEXT_SIZES.base,
    fontWeight: '600',
    color: '#FFFFFF',
    fontFamily: 'Inter',
  },
});
