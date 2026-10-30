// @ts-check
import { test, expect } from '@playwright/test';

const APP_URL = 'http://localhost:5175';

test.describe('Pallankuzhi app smoke tests', () => {
  test('renders game page and initial state', async ({ page }) => {
    await page.goto(APP_URL);

    await expect(page.getByRole('heading', { name: 'Pallankuzhi' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Player 1 Turn' })).toBeVisible();

    // There are 14 pits and each starts with 5 seeds.
    const pitText = page.getByTestId('pit');
    await expect(pitText).toHaveCount(14);
    await expect(pitText.first()).toHaveText('5');

    await expect(page.getByText('Player 1 Score: 0')).toBeVisible();
    await expect(page.getByText('Player 2 Score: 0')).toBeVisible();
  });

  test('moving from a pit calls API and switches player', async ({ page }) => {
    let moveCalled = false;
    await page.route('http://localhost:8000/moves/1', async route => {
      const request = route.request();
      // Debug log to confirm route is hit
      console.log('Route handler triggered for /moves/1');
      expect(request.method()).toBe('POST');
      const postData = JSON.parse(await request.postData() ?? '{}');
      expect(postData.start_index).toBe(0);
      expect(postData.player_turn).toBe(1);

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          board: [0, 6, 6, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5],
          scores: { '1': 1, '2': 0 },
          game_over: false,
          winner: null,
        }),
      });
    });

    page.on('request', req => {
      if (req.url().includes('/moves/1')) moveCalled = true;
    });

    await page.goto(APP_URL);

    const pits = page.getByTestId('pit');
    await expect(pits).toHaveCount(14);
    const playerOnePit = page.locator('[data-pit-index="0"]');
    console.log('playerOnePit count', await playerOnePit.count());
    await expect(playerOnePit).toBeVisible();
    await playerOnePit.scrollIntoViewIfNeeded();
    await playerOnePit.click({ force: true });

    // wait for request to backend to be made
    await page.waitForRequest('http://localhost:8000/moves/1', { timeout: 5000 });

    await expect(page.getByText('Player 1 Score: 1')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Player 2 Score: 0')).toBeVisible({ timeout: 10000 });
  });

  test('game over path shows winner alert', async ({ page }) => {
    let alertMessage = '';
    await page.route('http://localhost:8000/moves/1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          board: [0, 6, 6, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5],
          scores: { '1': 10, '2': 4 },
          game_over: true,
          winner: 'Player 1',
        }),
      });
    });

    page.on('dialog', dialog => {
      alertMessage = dialog.message();
      dialog.accept();
    });

    let moveCalled = false;
    page.on('request', req => {
      if (req.url().includes('/moves/1')) moveCalled = true;
    });

    await page.goto(APP_URL);

    const pits = page.getByTestId('pit');
    await expect(pits).toHaveCount(14);
    const playerOnePit = page.locator('[data-pit-index="0"]');
    await expect(playerOnePit).toBeVisible();
    await playerOnePit.click();

    await page.waitForRequest('http://localhost:8000/moves/1', { timeout: 5000 });
    await expect(alertMessage).toBe('Game Over! Winner: Player 1');
  });
});
